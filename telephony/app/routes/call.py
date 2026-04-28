import os
import sys
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response, FileResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
BASE_URL = os.getenv("BASE_URL")

@router.post("/incoming")
async def incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(num_digits=1, action=f"{BASE_URL}/call/handle-menu", method="POST")
    gather.play(f"{BASE_URL}/call/static/welcome")
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")

@router.post("/handle-menu")
async def handle_menu(request: Request):
    form = await request.form()
    digit = form.get("Digits", "1")
    response = VoiceResponse()
    response.play(f"{BASE_URL}/call/static/record_prompt")
    response.record(
        action=f"{BASE_URL}/call/process-recording?dtmf={digit}",
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
        # Download audio from Twilio
        audio_path = f"/tmp/recording_{dtmf}.wav"
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(
                f"{recording_url}.wav",
                auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            )
            with open(audio_path, "wb") as f:
                f.write(audio_response.content)

        # Send audio to Jeevan's AI server
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(audio_path, "rb") as audio_file:
                ai_response = await client.post(
                    "http://localhost:5001/call",
                    data={"dtmf": dtmf},
                    files={"audio": ("recording.wav", audio_file, "audio/wav")}
                )

        if ai_response.status_code == 200:
            # Save MP3 and play it
            out_path = f"/tmp/response_{dtmf}.mp3"
            with open(out_path, "wb") as f:
                f.write(ai_response.content)
            response.play(f"{BASE_URL}/call/audio/{dtmf}")
        else:
            response.play(f"{BASE_URL}/call/static/error")

    except Exception as e:
        print(f"Error: {e}")
        response.play(f"{BASE_URL}/call/static/error")

    return Response(content=str(response), media_type="application/xml")

@router.get("/audio/{dtmf}")
async def serve_audio(dtmf: str):
    path = f"/tmp/response_{dtmf}.mp3"
    return FileResponse(path, media_type="audio/mpeg")

@router.get("/static/{name}")
async def serve_static(name: str):
    path = f"/tmp/{name}.mp3"
    return FileResponse(path, media_type="audio/mpeg")
