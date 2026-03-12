"""
tutor_chat.py
-------------
Evaluates a user's answer using Google Gemini.
Provides scoring (0-100), verdict, deep explanation, and a pro tip.
"""

import json
import re
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_db import VectorDB

load_dotenv()


def safe_parse_json(raw: str) -> dict:
    """Robustly extract and parse JSON from Gemini response."""
    cleaned = raw.strip()
    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from Gemini response:\n{raw[:300]}")


class TutorChat:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        key_points: list,
        topic: str,
    ) -> dict:
        """Evaluate answer via Gemini — always fresh."""
        context = self.db.get_context(query=f"{topic} {question}", top_k=2)

        prompt = f"""You are an expert real estate tutor evaluating a student's quiz answer.

KNOWLEDGE BASE CONTEXT:
{context}

QUESTION:
{question}

STUDENT'S ANSWER:
{user_answer}

CORRECT ANSWER:
{correct_answer}

KEY CONCEPTS TO CHECK:
{chr(10).join(f"- {kp}" for kp in key_points)}

EVALUATION INSTRUCTIONS:
1. Score fairly — award partial credit for partially correct answers
2. Accept paraphrased answers that demonstrate understanding
3. A score of 80+ = correct, 40-79 = partial, 0-39 = incorrect
4. Explanation must teach, not just repeat the correct answer
5. Pro tip must be a real-world insider insight an experienced agent would know

CRITICAL: Your response must be a single valid JSON object only.
No explanation, no markdown, no code fences, no text before or after.

Output this exact structure:
{{
  "score": <integer 0-100>,
  "verdict": "correct" or "partial" or "incorrect",
  "short_feedback": "one concise sentence summarizing performance",
  "explanation": "2-3 sentences explaining the concept with real-world context",
  "pro_tip": "one insider tip an experienced real estate professional would add"
}}"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )

        result = safe_parse_json(response.text)
        result["correct_answer"] = correct_answer
        return result

    def get_followup_explanation(self, topic: str, concept: str) -> str:
        context = self.db.get_context(query=concept, top_k=2)
        prompt = f"""You are a friendly real estate tutor.

CONTEXT FROM KNOWLEDGE BASE:
{context}

A student is struggling to understand: "{concept}" (topic: {topic})

Give a clear, friendly explanation in 3-4 sentences using a simple analogy or real-world example.
Do NOT use jargon without explaining it. Write in plain English."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
