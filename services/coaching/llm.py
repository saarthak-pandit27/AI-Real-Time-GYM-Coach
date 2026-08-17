import logging
from services.config.workout_config import PROMPT

logger = logging.getLogger(__name__)


class LLMCoach:
    def __init__(self, groq_client=None):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT

    def _generate_fallback_feedback(self, event, issue):
        """Rule-based instant coach response if Groq API is unavailable or throws an error."""
        if event == "workout_started":
            return "Let's bring maximum energy! Focus on controlled movements, keep your core tight, and let's conquer this set!"
        elif event == "workout_completed":
            return "Outstanding workout! You crushed all your targets. Take time to stretch and stay hydrated!"
        elif event == "set_completed":
            return "Great set! Take a deep breath, reset your stance, and get ready for the next one."
        elif event == "no_pose_detected":
            return "Step into the camera frame so I can track your form and guide your reps."
        elif issue:
            return f"Form alert: {issue}. Adjust your alignment and stay strong!"
        else:
            return "Solid posture! Maintain that steady tempo."

    def give_feedback(self, event, issue=None):
        prompt = f"Event: {event}"
        if issue:
            prompt += f" Form Issue: {issue}"

        if not self.client:
            return self._generate_fallback_feedback(event, issue)

        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.history[-10:],
                {"role": "user", "content": prompt}
            ]

            candidate_models = [
                "openai/gpt-oss-20b",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768",
                "llama-3.3-70b-versatile"
            ]

            response = None
            last_err = None
            for model_name in candidate_models:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.4,
                        timeout=5.0
                    )
                    if response:
                        break
                except Exception as err:
                    last_err = err

            if not response:
                raise last_err or Exception("All candidate Groq models failed")

            text = response.choices[0].message.content.strip()
            self.history.append({"role": "assistant", "content": text})
            return text
        except Exception as e:
            logger.warning(f"Groq LLM feedback failed ({e}). Using rule-based coaching fallback.")
            return self._generate_fallback_feedback(event, issue)