import os
import tempfile
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from ai.diagnose import diagnose
from pipeline import run as pipeline_run
from tts import synthesise
from farmcast import transcribe, extract_crop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Lifespan: runs once at startup ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KisanSathi AI engine starting...")
    yield
    logger.info("KisanSathi AI engine stopped.")


app = FastAPI(
    title="KisanSathi AI",
    version="2.0.0",
    lifespan=lifespan,
)


# ── Request models ────────────────────────────────────────────
class DiagnoseTextRequest(BaseModel):
    symptom: str
    crop: str | None = None


# ── /health ───────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "kisansathi-ai"}


# ── /diagnose/text ────────────────────────────────────────────
@app.post("/diagnose/text")
def diagnose_text(body: DiagnoseTextRequest):
    if not body.symptom.strip():
        raise HTTPException(status_code=400, detail="symptom required")
    return diagnose(body.symptom, crop=body.crop)


# ── /diagnose/audio ───────────────────────────────────────────
@app.post("/diagnose/audio")
async def diagnose_audio(audio: UploadFile = File(...)):
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name
    try:
        transcript = transcribe(tmp_path)
        crop = extract_crop(transcript)
        result = diagnose(transcript, crop=crop)
        result["transcript"] = transcript
        result["detected_crop"] = crop
        return result
    finally:
        os.unlink(tmp_path)


# ── /call  (main Exotel endpoint) ─────────────────────────────
@app.post("/call")
async def call(
    audio: UploadFile = File(...),
    dtmf: str = Form(...),
    audio2: UploadFile = File(None),
):
    """
    Exotel sends:
      - audio  : farmer's first recording (required)
      - dtmf   : IVR keypress "1"-"5" (required)
      - audio2 : farmer's second recording (optional, only on retry)

    Returns: Kannada MP3 audio bytes
    """
    # ── Transcribe round 1 ────────────────────────────────────
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    transcript_1 = None
    transcript_2 = None

    try:
        transcript_1 = transcribe(tmp_path)
        logger.info(f"Transcript 1: {transcript_1}")
    finally:
        os.unlink(tmp_path)

    # ── Transcribe round 2 if present ────────────────────────
    if audio2:
        suffix2 = os.path.splitext(audio2.filename or "audio.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix2, delete=False) as tmp2:
            tmp2.write(await audio2.read())
            tmp2_path = tmp2.name
        try:
            transcript_2 = transcribe(tmp2_path)
            logger.info(f"Transcript 2: {transcript_2}")
        finally:
            os.unlink(tmp2_path)

    # ── Run pipeline ──────────────────────────────────────────
    result = pipeline_run(dtmf, transcript_1, transcript_2)
    logger.info(f"Pipeline result: intent={result.get('intent')} status={result.get('status')}")

    # ── Needs retry — return retry prompt as audio ────────────
    if result.get("needs_retry"):
        retry_text = result.get("retry_prompt", "")
        audio_bytes = synthesise(retry_text)
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="TTS failed on retry prompt")
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"X-Needs-Retry": "true"},
        )

    # ── Normal response ───────────────────────────────────────
    kannada_text = result.get("response_kannada", "")
    if not kannada_text:
        raise HTTPException(status_code=500, detail="No Kannada response from pipeline")

    audio_bytes = synthesise(kannada_text)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="TTS synthesis failed")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"X-Needs-Retry": "false"},
    )


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=5001, reload=False)
