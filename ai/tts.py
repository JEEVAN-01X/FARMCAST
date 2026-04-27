import os
import io
import logging
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── Translate English → Kannada using LLaMA ──────────────────
def to_kannada(text: str) -> str:
    """
    Translates English text to Kannada.
    Only call this if you don't already have Kannada text.
    pipeline.py already provides response_kannada — use synthesise() directly.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": (
                    "Translate this to Kannada language only. "
                    "Return only the Kannada text, nothing else:\n\n"
                    + text
                )
            }],
            max_tokens=200,
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"to_kannada translation failed: {e}")
        return text  # fallback — return original if translation fails


# ── Convert Kannada text → audio bytes ───────────────────────
def synthesise(kannada_text: str) -> bytes | None:
    """
    Main function called by api.py.
    Input : Kannada text string (already translated)
    Output: MP3 audio bytes — api.py sends this to Exotel
    Returns None on failure.
    """
    try:
        tts = gTTS(text=kannada_text, lang="kn", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"gTTS synthesis failed: {e}")
        return None


# ── Combined: English → Kannada → audio bytes ────────────────
def speak_kannada(english_text: str) -> bytes | None:
    """
    Convenience function.
    Use this only when you have English text and need audio.
    For pipeline output use synthesise(response_kannada) directly.
    """
    kannada = to_kannada(english_text)
    logger.info(f"Kannada translation: {kannada}")
    return synthesise(kannada)


# ── Standalone test ───────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("\n" + "="*60)
    print("TTS — TEST RUN")
    print("="*60)

    # Test 1 — synthesise already-translated Kannada
    print("\nTest 1: synthesise() with Kannada text")
    kannada = "Sir, nimge PM-KISAN scheme sigatte. Pratii varsha aaru saavira rupai nimma account ge barthade."
    audio = synthesise(kannada)
    if audio:
        with open("/tmp/test_tts_1.mp3", "wb") as f:
            f.write(audio)
        print(f"Audio bytes: {len(audio)} | Saved to /tmp/test_tts_1.mp3")
    else:
        print("FAILED")

    # Test 2 — speak_kannada with English input
    print("\nTest 2: speak_kannada() with English text")
    audio2 = speak_kannada("Spray Chlorpyrifos on the stem immediately to treat stem borer disease.")
    if audio2:
        with open("/tmp/test_tts_2.mp3", "wb") as f:
            f.write(audio2)
        print(f"Audio bytes: {len(audio2)} | Saved to /tmp/test_tts_2.mp3")
    else:
        print("FAILED")

    print("\nDone. Check /tmp/test_tts_1.mp3 and /tmp/test_tts_2.mp3")
