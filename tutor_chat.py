"""
tutor_chat.py
-------------
Evaluates MCQ answers and provides detailed explanations with
real-world examples when the answer is incorrect.
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
    raise ValueError(f"Could not parse JSON:\n{raw[:300]}")


class TutorChat:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def evaluate_answer(
        self,
        question: str,
        options: dict,
        selected_option: str,
        correct_option: str,
        topic: str,
    ) -> dict:
        """
        Evaluate MCQ answer.
        If correct  → short congratulation + brief explanation
        If incorrect → detailed explanation with real-world example
        """
        is_correct = selected_option.upper() == correct_option.upper()
        correct_text = options.get(correct_option, "")
        selected_text = options.get(selected_option, "")
        context = self.db.get_context(query=f"{topic} {question}", top_k=2)

        if is_correct:
            prompt = f"""You are a friendly real estate tutor.

CONTEXT: {context}

The student answered this MCQ CORRECTLY:
Question: {question}
Their answer: {selected_option}. {selected_text}

Give a SHORT congratulation and a 1-2 sentence explanation of WHY this answer is correct.
Keep it simple, friendly, encouraging.
Max 40 words total.

RETURN ONLY THIS JSON:
{{
  "verdict": "correct",
  "score": 100,
  "short_feedback": "one encouraging sentence",
  "explanation": "1-2 sentences why this is correct",
  "real_world_example": "",
  "remember_tip": "one short memory tip max 15 words"
}}"""
        else:
            prompt = f"""You are a friendly real estate tutor helping a beginner learn.

CONTEXT: {context}

The student answered this MCQ INCORRECTLY:
Question: {question}
Options:
A. {options.get('A','')}
B. {options.get('B','')}
C. {options.get('C','')}
D. {options.get('D','')}

Student chose: {selected_option}. {selected_text}
Correct answer: {correct_option}. {correct_text}

Your job: Explain this in a way that ANYONE can understand, even with zero real estate knowledge.

RULES:
- Be kind and encouraging, never discouraging
- Explain the concept from scratch in simple words
- Give a real-world everyday example (like comparing to buying groceries, renting a car, etc.)
- Tell them exactly why their answer was wrong
- Tell them why the correct answer is right
- End with an easy memory tip

RETURN ONLY THIS JSON:
{{
  "verdict": "incorrect",
  "score": 0,
  "short_feedback": "kind one sentence response to wrong answer",
  "explanation": "2-3 simple sentences explaining the correct concept from scratch",
  "real_world_example": "a relatable everyday example that makes this concept crystal clear",
  "remember_tip": "a fun easy way to remember this, max 20 words"
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
        result["correct_option"] = correct_option
        result["correct_text"] = correct_text
        result["selected_option"] = selected_option
        result["selected_text"] = selected_text
        return result