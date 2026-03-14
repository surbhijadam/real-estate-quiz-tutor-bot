"""
quiz_generator.py
-----------------
Generates MCQ questions with 4 options using Google Gemini + RAG.
"""

import json
import re
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from vector_db import VectorDB

load_dotenv()

TOPICS = [
    "MLS Listings & Terminology",
    "Property Valuation",
    "Listing Agreements",
    "Cap Rates & ROI",
    "Property Types",
    "Legal Disclosures",
    "Days on Market",
    "Comparative Market Analysis",
    "Earnest Money & Contingencies",
    "Closing Costs",
]


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


class QuizGenerator:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate_question(self, topic: str, difficulty: str = "beginner") -> dict:
        """Generate a fresh MCQ question with 4 options every time."""
        context = self.db.get_context(query=topic, top_k=3)

        prompt = f"""You are a friendly real estate quiz creator making beginner-friendly MCQ questions.

KNOWLEDGE BASE CONTEXT:
{context}

TOPIC: "{topic}"

Create a simple multiple choice question about this topic that anyone can understand.

STRICT RULES:
- Question: max 20 words, simple English
- 4 options labeled A, B, C, D
- Each option: max 10 words
- Only ONE correct answer
- Wrong options should be plausible but clearly wrong
- correct_option must be exactly "A", "B", "C", or "D"
- hint: max 12 words

RETURN ONLY THIS JSON:
{{
  "question": "short simple question here?",
  "options": {{
    "A": "first option text",
    "B": "second option text",
    "C": "third option text",
    "D": "fourth option text"
  }},
  "correct_option": "A",
  "hint": "short hint here",
  "topic": "{topic}",
  "difficulty": "beginner"
}}"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=2048,
            )
        )
        return safe_parse_json(response.text)