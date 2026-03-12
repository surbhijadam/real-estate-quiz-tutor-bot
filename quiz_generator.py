"""
quiz_generator.py
-----------------
Uses RAG (VectorDB) + Google Gemini to generate contextually
grounded quiz questions from the real estate knowledge base.
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

DIFFICULTY_GUIDE = {
    "beginner"    : "simple definitional question, single concept, no calculations",
    "intermediate": "applied question requiring understanding of how concepts work together",
    "advanced"    : "scenario-based question, may require calculation or multi-step reasoning",
}


def safe_parse_json(raw: str) -> dict:
    """Robustly extract and parse JSON from Gemini response."""
    cleaned = raw.strip()
    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    # Step 1 — direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 2 — extract JSON block via regex
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from Gemini response:\n{raw[:300]}")


class QuizGenerator:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate_question(self, topic: str, difficulty: str = "intermediate") -> dict:
        """Generate a fresh question every time."""
        context = self.db.get_context(query=topic, top_k=3)
        difficulty_note = DIFFICULTY_GUIDE.get(difficulty, DIFFICULTY_GUIDE["intermediate"])

        prompt = f"""You are a real estate quiz question generator.

CONTEXT:
{context}

Generate a {difficulty} quiz question about "{topic}".
Difficulty: {difficulty_note}

STRICT LENGTH RULES:
- "question": max 20 words
- "hint": max 15 words
- "correct_answer": max 40 words
- "key_points": exactly 3 items, max 5 words each

CRITICAL: Return ONLY this JSON, nothing else:
{{
  "question": "short question here",
  "hint": "short hint here",
  "correct_answer": "concise answer here",
  "key_points": ["point 1", "point 2", "point 3"],
  "topic": "{topic}",
  "difficulty": "{difficulty}"
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
