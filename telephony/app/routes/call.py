import os
import sys
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response, FileResponse
from twilio.twiml.voice_response import VoiceResponse, Gather, Record
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, "/home/jeevan__x/Desktop/FARMCAST/ai")
import pipeline
import tts

router = APIRouter()

BASE_URL = os.getenv("BASE_URL")

@router.post("/incoming")
async def incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(num_digits=1, action="/call/handle-menu", method="POST")
    gather.say(
        "FarmCast ge swagata. "
        "Roga problem ge one. "
        "Bele price ge two. "
        "Yojane bekandre three. "
        "Havamana bekandre four. "
        "Bere vishaya bekandre five.",
        language="kn-IN"
    )
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")

@router.post("/handle-menu")
async def handle_menu(request: Request):
    form = await request.form()
    digit = form.get("Digits", "1")
    response = VoiceResponse()

    response.say("Beep nantara matadi.", language="kn-IN")
    response.record(
        action=f"/call/process-recording?dtmf={digit}",
        method="POST",
        max_length=15,
        finish_on_key="#",
        play_beep=True
    )
    return Response(content=str(response), media_type="application/xml")

@router.post("/process-recording")
async def process_recording(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl")
    dtmf = request.query_params.get("dtmf", "1")
    response = VoiceResponse()

    try:
        audio_path = f"/tmp/recording_{dtmf}.wav"
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(
                f"{recording_url}.wav",
                auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            )
            with open(audio_path, "wb") as f:
                f.write(audio_response.content)

        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language="kn"
            )
        transcript = transcription.text

        result = pipeline.run(dtmf, transcript)
        kannada_text = result.get("response_kannada", "Kshamisiri, matte try madi.")

        audio_bytes = tts.synthesise(kannada_text)
        if audio_bytes:
            out_path = f"/tmp/response_{dtmf}.mp3"
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            response.play(f"{BASE_URL}/call/audio/{dtmf}")
        else:
            response.say(kannada_text, language="kn-IN")

    except Exception as e:
        print(f"Error: {e}")
        response.say("Kshamisiri, technical problem agide. Matte call madi.", language="kn-IN")

    return Response(content=str(response), media_type="application/xml")

@router.get("/audio/{dtmf}")
async def serve_audio(dtmf: str):
    path = f"/tmp/response_{dtmf}.mp3"
    return FileResponse(path, media_type="audio/mpeg")
