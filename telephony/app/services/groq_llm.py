import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def get_ai_response(query: str, category: str) -> str:
    prompts = {
        "1": f"""You are Kisan Sathi, an agricultural assistant for Karnataka farmers.
A farmer has described a crop problem: {query}
Respond in simple Kannada. Give:
1. Disease name
2. Simple treatment in 2 lines
3. Common medicine name
Keep response under 50 words.""",

        "2": f"""You are Kisan Sathi, an agricultural assistant for Karnataka farmers.
A farmer is asking about mandi price for: {query}
Respond in simple Kannada. Give today's approximate price per quintal.
Keep response under 30 words.""",

        "3": f"""You are Kisan Sathi, an agricultural assistant for Karnataka farmers.
A farmer is asking about government schemes: {query}
Respond in simple Kannada. Name the most relevant scheme and one key benefit.
Keep response under 40 words.""",

        "4": f"""You are Kisan Sathi, an agricultural assistant for Karnataka farmers.
A farmer is asking about market demand: {query}
Respond in simple Kannada. Give next season crop recommendation.
Keep response under 30 words."""
    }

    prompt = prompts.get(category, prompts["1"])

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content
