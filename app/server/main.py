import os
import sys
import httpx
from dotenv import load_dotenv
import inngest
import inngest.fast_api
from fastapi import FastAPI, status, Request


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.server.schemas import ChatRequest, ChatResponse
from app.server.event import inngest_client
from app.server.workers import background_worker

app = FastAPI(title="Leadway Assurance Core Production RAG API",
    description="Asynchronous edge-optimized API handling consumer policy matching queries.")

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_message(chat_id: str, text: str):
    url = f"{TELEGRAM_API}/sendMessage"

    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]

    async with httpx.AsyncClient() as client:
        for chunk in chunks:
            await client.post(url, json={
                "chat_id": chat_id,
                "text": chunk
            })


async def send_typing(chat_id: str):
    url = f"{TELEGRAM_API}/sendChatAction"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "action": "typing"})

@app.post("/api/chat", response_model= ChatResponse, status_code= status.HTTP_202_ACCEPTED)
async def submit_user_chat(request_payload: ChatRequest):
    """
    Primary Consumer Entryway. Accepts real-time chat input strings, enforces 
    Pydantic schema constraints, hands the payload off to the background queue, 
    and instantly responds back to keep the connection line lightning fast.
    """
    payload = request_payload.model_dump()

    await inngest_client.send(
        inngest.Event(
            name= "check_incoming_status",
            data= payload
        )   
    )

    return ChatResponse(
        status="queued",
        message="Your Leadway insurance query has been successfully received and is currently being processed."
    )


@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return {"status": "ignored"}

    chat_id = str(data["message"]["chat"]["id"])
    user_text = data["message"].get("text", "")

    if not user_text.strip():
        return {"status": "ignored"}


    await send_typing(chat_id)

    try:
        validated_data = ChatRequest(user_id=chat_id, message=user_text)
    except Exception as e:
        await send_message(chat_id, "⚠️ Your message is too long or invalid.")
        return {"status": "validation_error"}

    await inngest_client.send(
        inngest.Event(
            name="check_incoming_status",
            data=validated_data.model_dump()
        )   
    )

    await send_message(chat_id, "⏳ Processing your insurance query...")

    return {"status": "ok"}

inngest.fast_api.serve(app, inngest_client, [background_worker])