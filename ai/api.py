import os
import tempfile
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from diagnose import diagnose
from pipeline import run_pipeline
from tts import synthesise

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
    result = diagnose(body.symptom, crop=body.crop)
    return result


# ── /diagnose/audio ───────────────────────────────────────────
@app.post("/diagnose/audio")
async def diagnose_audio(audio: UploadFile = File(...)):
    from pipeline import transcribe_audio, extract_crop_from_text

    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        transcript = transcribe_audio(tmp_path)
        crop = extract_crop_from_text(transcript)
        result = diagnose(transcript, crop=crop)
        result["transcript"] = transcript
        result["detected_crop"] = crop
        return result
    finally:
        os.unlink(tmp_path)


# ── /call  (main Exotel endpoint) ─────────────────────────────
@app.post("/call")
async def call(audio: UploadFile = File(...)):
    """
    Exotel sends farmer's audio here.
    Returns Kannada MP3 audio bytes directly.
    """
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        pipeline_result = run_pipeline(tmp_path)
        kannada_text = pipeline_result.get("response_kannada", "")

        if not kannada_text:
            raise HTTPException(
                status_code=500,
                detail="Pipeline returned no Kannada response"
            )

        audio_bytes = synthesise(kannada_text)

        if not audio_bytes:
            raise HTTPException(
                status_code=500,
                detail="TTS synthesis failed"
            )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
        )
    finally:
        os.unlink(tmp_path)


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=5001, reload=False)
