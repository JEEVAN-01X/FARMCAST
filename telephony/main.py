from fastapi import FastAPI
from app.routes.call import router as call_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Kisan Sathi Telephony")

app.include_router(call_router, prefix="/call")

@app.get("/")
def health_check():
    return {"status": "Kisan Sathi telephony server is running"}
