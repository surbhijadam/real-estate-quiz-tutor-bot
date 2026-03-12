"""
tutor_chat.py
-------------
Evaluates a user's answer using Google Gemini (free).
Provides scoring (0-100), verdict, deep explanation, and a pro tip.
Includes caching and rate limiting to handle quota constraints.
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from vector_db import VectorDB
from cache_manager import (
    get_cached_evaluation,
    cache_evaluation,
    RateLimiter,
)

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class TutorChat:
    def __init__(self, vector_db: VectorDB):
        self.db = vector_db
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
        self.rate_limiter = RateLimiter(initial_delay=2.0, max_retries=3)

    def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        key_points: list,
        topic: str,
    ) -> dict:
        # Check cache first
        cached = get_cached_evaluation(question, user_answer)
        if cached:
            print(f"📖 Using cached evaluation for this answer")
            return cached
        
        # Generate new evaluation with rate limiting
        try:
            result = self.rate_limiter.call_with_backoff(
                self._evaluate_answer_api,
                question,
                user_answer,
                correct_answer,
                key_points,
                topic
            )
            cache_evaluation(question, user_answer, result)
            return result
        except ResourceExhausted:
            print(f"⚠️  API quota exhausted. Using offline evaluation mode.")
            return self._offline_evaluation(user_answer, correct_answer, key_points)
        except Exception as e:
            print(f"❌ Error evaluating answer: {str(e)}")
            print(f"⚠️  Using offline evaluation mode.")
            return self._offline_evaluation(user_answer, correct_answer, key_points)

    def _offline_evaluation(self, user_answer: str, correct_answer: str, key_points: list) -> dict:
        """Provide offline evaluation when API is unavailable."""
        user_lower = user_answer.lower().strip()
        correct_lower = correct_answer.lower().strip()
        
        # Simple heuristic: check if user's answer contains key concepts
        matching_points = sum(1 for kp in key_points if kp.lower() in user_lower)
        coverage = matching_points / len(key_points) if key_points else 0
        
        if coverage >= 0.7:
            score = 75
            verdict = "partial"
            feedback = "Your answer covers most key concepts. Compare with the correct answer above for completeness."
        elif coverage >= 0.4:
            score = 50
            verdict = "partial"
            feedback = "Your answer addresses some key points but is missing important concepts."
        else:
            score = 30
            verdict = "incorrect"
            feedback = "Your answer doesn't cover the key concepts needed."
        
        return {
            "score": score,
            "verdict": verdict,
            "short_feedback": feedback,
            "explanation": "AI evaluation is temporarily unavailable. Review the correct answer and key concepts above to understand this topic better.",
            "pro_tip": "In real estate practice, mastering these concepts is essential for client interactions and negotiations.",
            "correct_answer": correct_answer
        }

    def _evaluate_answer_api(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        key_points: list,
        topic: str,
    ) -> dict:
        """Internal method to evaluate answer via API."""
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

Respond ONLY with valid JSON (no markdown, no extra text, no code fences):
{{
  "score"         : <integer 0-100>,
  "verdict"       : "correct" | "partial" | "incorrect",
  "short_feedback": "one concise sentence summarizing performance",
  "explanation"   : "2-3 sentences: explain the concept deeply with real-world context",
  "pro_tip"       : "one insider tip an experienced real estate professional would add"
}}"""

        response = self.model.generate_content(prompt)
        raw = response.text.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned)

        result["correct_answer"] = correct_answer
        return result

    def get_followup_explanation(self, topic: str, concept: str) -> str:
        try:
            return self.rate_limiter.call_with_backoff(
                self._get_followup_explanation_api,
                topic,
                concept
            )
        except ResourceExhausted:
            print(f"⚠️  API quota exhausted. Using offline explanation mode.")
            return f"The API is temporarily unavailable. Please review the course materials on '{concept}' under the '{topic}' section to deepen your understanding of this concept."
        except Exception as e:
            print(f"❌ Error getting explanation: {str(e)}")
            return f"Unable to generate explanation at this time. Please review the course materials on '{concept}' to learn more."

    def _get_followup_explanation_api(self, topic: str, concept: str) -> str:
        """Internal method to get followup explanation via API."""
        context = self.db.get_context(query=concept, top_k=2)

        prompt = f"""You are a friendly real estate tutor.

CONTEXT FROM KNOWLEDGE BASE:
{context}

A student is struggling to understand: "{concept}" (topic: {topic})

Give a clear, friendly explanation in 3-4 sentences using a simple analogy or real-world example.
Do NOT use jargon without explaining it. Write in plain English."""

        response = self.model.generate_content(prompt)
        return response.text.strip()