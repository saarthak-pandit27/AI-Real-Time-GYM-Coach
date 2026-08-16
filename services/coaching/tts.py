from io import BytesIO
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)


class TextToSpeech:
    def speak(self, text, lang="en"):
        cleaned = (text or "").strip()

        if not cleaned:
            return None
        
        try:
            buffer = BytesIO()
            gTTS(text=cleaned, lang=lang).write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            logger.warning(f"gTTS audio synthesis failed ({e}). Web speech synthesis will trigger as fallback.")
            return None