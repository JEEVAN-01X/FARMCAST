import os
import httpx

async def text_to_speech(text: str, output_path: str) -> str:
    url = "https://translate.google.com/translate_tts"
    params = {
        "ie": "UTF-8",
        "q": text,
        "tl": "kn",
        "client": "tw-ob"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers={
            "User-Agent": "Mozilla/5.0"
        })
        
        with open(output_path, "wb") as f:
            f.write(response.content)
    
    return output_path

