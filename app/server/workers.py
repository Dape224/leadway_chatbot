import os
import sys
import httpx
import requests
from dotenv import load_dotenv
import inngest


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.rag_engine import get_embedded_response
from app.server.event import inngest_client


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"



async def send_message(chat_id: str, text: str):
    url = f"{TELEGRAM_API}/sendMessage"

    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]

    async with httpx.AsyncClient() as client:
        for chunk in chunks:
            try:
                await client.post(url, json={
                    "chat_id": chat_id,
                    "text": chunk
                }, timeout=15.0)
            except Exception as e:
                print(f"❌ Failed sending chunk to Telegram: {e}")


@inngest_client.create_function(fn_id= "execute_leadway_rag", trigger= inngest.TriggerEvent(event= "check_incoming_status"))
async def background_worker(ctx: inngest.Context):
    """
    Durable Background Worker.
    This wakes up automatically whenever a 'chat/message_submitted' event hits the bus.
    It handles the slow RAG database lookup safely away from the main thread.
    """
    user_no = ctx.event.data.get("user_id")
    if not user_no:
        return {"status": "failed", "error": "Missing user_id"}
    user_query = ctx.event.data.get("message")

    print(f"📡 Worker Active: Processing question for Session ID {user_no}...")

    try:
        async def run_rag():
            query_engine = get_embedded_response()
            result = query_engine.query(user_query)
            return str(result) if result else "⚠️ No response generated."

        final_response = await ctx.step.run("execute_rag_lookup", run_rag)

        print(f"✅ RAG Processing Complete for Session ID {user_no}!")

        await send_message(user_no, final_response)
        print("Sending message to Telegram:", final_response)

        return {
            "status": "success",
            "user_id": user_no,
            "message": final_response
        }

    except Exception as e:
        if "429" in str(e):
            reply = "⏳ Too many requests. Please wait a few seconds and try again."
        else:
            reply = "⚠️ Something went wrong. Try again later."
        send_message(user_no, reply)

        return {
            "status": "error",
            "user_id": user_no,
            "message": reply
        }

