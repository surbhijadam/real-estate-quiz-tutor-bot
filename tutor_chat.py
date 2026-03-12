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

        prompt = f"""You are a real estate tutor evaluating a student's answer.

CONTEXT: {context}

QUESTION: {question}
STUDENT ANSWER: {user_answer}
CORRECT ANSWER: {correct_answer}
KEY POINTS: {", ".join(key_points)}

SCORING: 80+ = correct, 40-79 = partial, 0-39 = incorrect
Award partial credit for paraphrased or near-correct answers.

STRICT LENGTH RULES:
- "short_feedback": max 15 words
- "explanation": max 40 words
- "pro_tip": max 20 words

CRITICAL: Return ONLY this JSON, nothing else:
{{
  "score": <integer 0-100>,
  "verdict": "correct" or "partial" or "incorrect",
  "short_feedback": "brief feedback here",
  "explanation": "concise explanation here",
  "pro_tip": "short insider tip here"
}}"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4096,
            )
        )

        result = safe_parse_json(response.text)
        result["correct_answer"] = correct_answer
        return result

    def get_followup_explanation(self, topic: str, concept: str) -> str:
        context = self.db.get_context(query=concept, top_k=2)
        prompt = f"""You are a friendly real estate tutor.
CONTEXT: {context}
Explain "{concept}" (topic: {topic}) in 3-4 simple sentences with a real-world analogy."""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()