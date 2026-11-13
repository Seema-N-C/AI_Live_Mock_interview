import io
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

load_dotenv()
client = Groq()  # reads GROQ_API_KEY from environment


def transcribe(audio_bytes: bytes):
    """Speech to text. Returns (text, segments) where segments = [{'start','end'}]."""
    r = client.audio.transcriptions.create(
        file=("answer.wav", audio_bytes),
        model="whisper-large-v3",
        response_format="verbose_json",
        language="en",
    )
    segs = []
    for s in (getattr(r, "segments", None) or []):
        if isinstance(s, dict):
            segs.append({"start": s["start"], "end": s["end"]})
        else:
            segs.append({"start": s.start, "end": s.end})
    return r.text.strip(), segs


def speak(text: str):
    """Text to speech (Indian English). Returns mp3 bytes, or None on failure."""
    try:
        buf = io.BytesIO()
        gTTS(text[:500], lang="en", tld="co.in").write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None
