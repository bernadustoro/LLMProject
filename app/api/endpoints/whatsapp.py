import os
import httpx
from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException

router = APIRouter()

async def send_wa_message(phone_number_id: str, to_number: str, text_message: str):
    """Fungsi pembantu untuk mengirim pesan balasan ke WhatsApp Meta API"""
    wa_token = os.getenv("WHATSAPP_TOKEN")
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {wa_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "text": {"body": text_message}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)

async def process_and_reply_wa_v2(phone_number_id: str, from_number: str, user_message: str):
    """Proses pesan WA menggunakan pendekatan V2 (Inject Semua Data)"""
    try:
        async with httpx.AsyncClient() as client:
            # Menembak langsung ke endpoint V2 lokal
            response = await client.post(
                "https://llmproject-production.up.railway.app/api/v2/items/ask",
                json={"question": user_message},
                timeout=30.0 # Beri waktu agar AI sempat berpikir
            )
            response.raise_for_status()
            data = response.json()
            answer_text = data.get("answer", "Maaf, AI tidak mengembalikan jawaban.")
    except Exception as e:
        answer_text = f"Maaf, sistem V2 sedang mengalami gangguan: {str(e)}"
        
    await send_wa_message(phone_number_id, from_number, answer_text)

async def process_and_reply_wa_v3(phone_number_id: str, from_number: str, user_message: str):
    """Proses pesan WA menggunakan pendekatan V3 (LangGraph Agent)"""
    try:
        async with httpx.AsyncClient() as client:
            # Menembak langsung ke endpoint V3 lokal
            response = await client.post(
                "https://llmproject-production.up.railway.app/api/v3/agent/ask",
                json={"question": user_message},
                timeout=30.0 # Beri waktu agar AI sempat berpikir
            )
            response.raise_for_status()
            data = response.json()
            answer_text = data.get("answer", "Maaf, AI tidak mengembalikan jawaban.")
    except Exception as e:
        answer_text = f"Maaf, sistem V3 sedang mengalami gangguan: {str(e)}"
        
    await send_wa_message(phone_number_id, from_number, answer_text)

# Endpoint GET untuk verifikasi Webhook Meta (berlaku untuk v2 dan v3)
@router.get("/v2/webhook")
@router.get("/v3/webhook")
async def verify_whatsapp_webhook(request: Request):
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Invalid verify token")

async def handle_wa_webhook(request: Request, background_tasks: BackgroundTasks, process_func):
    """Fungsi umum untuk mem-parsing JSON dari Meta WhatsApp API"""
    data = await request.json()
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    for message in value["messages"]:
                        if message.get("type") == "text":
                            phone_number_id = value["metadata"]["phone_number_id"]
                            from_number = message["from"]
                            text_body = message["text"]["body"]
                            background_tasks.add_task(process_func, phone_number_id, from_number, text_body)
    except Exception as e:
        print(f"Error parsing WA Webhook: {e}")
    return {"status": "ok"}

@router.post("/v2/webhook")
async def receive_wa_v2(request: Request, background_tasks: BackgroundTasks):
    return await handle_wa_webhook(request, background_tasks, process_and_reply_wa_v2)

@router.post("/v3/webhook")
async def receive_wa_v3(request: Request, background_tasks: BackgroundTasks):
    return await handle_wa_webhook(request, background_tasks, process_and_reply_wa_v3)