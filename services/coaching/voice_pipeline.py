import time
import streamlit as st
import streamlit.components.v1 as components
import json
import logging

logger = logging.getLogger(__name__)


class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0

    def _find_form_issue(self, exercise, metrics):
        if "issue" in metrics:
            return metrics["issue"]

        if exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)
            
            if depth == "TOO HIGH":
                return "The user's squat is not deep enough — knees are not bending sufficiently."

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "The user is leaning too far forward during the squat."

        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")
            
            if alignment == "Poor Form":
                return "The user's body is not straight during the push-up."

            if hip_status == "SAGGING":
                return "The user's hips are sagging down during the push-up."

            if hip_status == "PIKED UP":
                return "The user's hips are too high — lower them to form a straight line."

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")
            
            if swing == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."

        elif exercise == "Shoulder Press":
            back_arch = metrics.get("back_arch_status", "")
            
            if back_arch == "Excessive Arch":
                return "The user is arching their lower back excessively during the press."

            if back_arch == "Slight Arch":
                return "Slight back arch detected — encourage the user to brace their core."

        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")
            
            if balance == "OFF BALANCE":
                return "The user is losing balance during the lunge — feet should be hip-width apart."

        return None

    def process_event(self, event, exercise, metrics):
        try:
            issue = self._find_form_issue(exercise, metrics)
            now = time.time()
            is_major_issue = event in ["workout_started", "set_completed", "workout_completed"]

            if not is_major_issue:
                if not issue:
                    return None
                
                if now - self.last_spoken_at < 5:
                    return None
                
            text = self.llm.give_feedback(event, issue) if self.llm else "Let's push hard and keep solid posture!"
            voice = self.tts.speak(text) if self.tts else None

            self.last_spoken_at = now
            return voice, text
        except Exception as e:
            logger.error(f"Error processing voice event {event}: {e}")
            fallback_text = f"Workout {event.replace('_', ' ')}! Stay focused and keep solid form."
            return None, fallback_text


def autoplay_audio(audio_bytes, text_fallback=None):
    """Play audio bytes or use Web Speech API fallback."""
    if audio_bytes:
        try:
            st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            return
        except Exception as e:
            logger.warning(f"st.audio playback failed: {e}")

    # Fallback to browser Web Speech API JS if audio_bytes is absent or failed
    if text_fallback:
        escaped_text = json.dumps(text_fallback)
        components.html(
            f"""
            <script>
            (function() {{
                try {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utterance = new SpeechSynthesisUtterance({escaped_text});
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        utterance.volume = 1.0;
                        window.speechSynthesis.speak(utterance);
                    }}
                }} catch (err) {{
                    console.warn('Web speech synthesis failed:', err);
                }}
            }})();
            </script>
            """,
            height=0,
        )