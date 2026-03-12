"""
quiz_generator.py
-----------------
Uses RAG (VectorDB) + Google Gemini (free) to generate contextually
grounded quiz questions from the real estate knowledge base.
Includes caching and rate limiting to handle quota constraints.
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from vector_db import VectorDB
from cache_manager import (
    get_cached_question,
    cache_question,
    RateLimiter,
)
from fallback_questions import get_fallback_question

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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


class QuizGenerator:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
        )
        self.rate_limiter = RateLimiter(initial_delay=2.0, max_retries=3)

    def generate_question(self, topic: str, difficulty: str = "intermediate") -> dict:
        # Check cache first
        cached = get_cached_question(topic, difficulty)
        if cached:
            print(f"📚 Using cached question for {topic} ({difficulty})")
            return cached
        
        # Try to generate new question with rate limiting
        try:
            question_data = self.rate_limiter.call_with_backoff(
                self._generate_new_question,
                topic,
                difficulty
            )
            cache_question(topic, difficulty, question_data)
            return question_data
        except ResourceExhausted as e:
            print(f"⚠️  API quota exhausted. Using offline fallback question.")
            fallback = get_fallback_question(topic, difficulty)
            return fallback
        except Exception as e:
            print(f"❌ Error generating question: {str(e)}")
            print(f"⚠️  Falling back to offline question.")
            fallback = get_fallback_question(topic, difficulty)
            return fallback

    def _generate_new_question(self, topic: str, difficulty: str) -> dict:
        """Internal method to generate a new question via API."""
        context = self.db.get_context(query=topic, top_k=3)
        difficulty_note = DIFFICULTY_GUIDE.get(difficulty, DIFFICULTY_GUIDE["intermediate"])

        prompt = f"""You are an expert real estate educator creating assessment questions.

KNOWLEDGE BASE CONTEXT (use this as the source of truth):
{context}

TASK:
Generate a {difficulty} difficulty quiz question about: "{topic}"
Difficulty note: {difficulty_note}

RULES:
- Question must be answerable from the context above
- Do not ask yes/no questions
- Be specific and practical

Respond ONLY with valid JSON (no markdown, no extra text, no code fences):
{{
  "question"      : "the full question text",
  "hint"          : "a subtle hint that nudges without giving away the answer",
  "correct_answer": "the ideal complete answer",
  "key_points"    : ["key concept 1", "key concept 2", "key concept 3"],
  "topic"         : "{topic}",
  "difficulty"    : "{difficulty}"
}}"""

        response = self.model.generate_content(prompt)
        raw = response.text.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)