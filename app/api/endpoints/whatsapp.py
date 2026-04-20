import os
import httpx
from fastapi import APIRouter, Request, Response, BackgroundTasks

router = APIRouter()

async def send_twilio_message(to_number: str, text_message: str):
    """Fungsi pembantu untuk mengirim pesan balasan via Twilio API"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")  # cth: "whatsapp:+14155238886"
    
    if not all([account_sid, auth_token, from_number]):
        print("!!! [FATAL] Kredensial Twilio tidak lengkap di environment.", flush=True)
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    # Twilio API menggunakan URL-encoded form data (bukan JSON)
    payload = {
        "To": to_number,
        "From": from_number,
        "Body": text_message
    }
    
    print(f"--> [SEND TWILIO] Mencoba mengirim ke {to_number}...", flush=True)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, auth=(account_sid, auth_token))
            response.raise_for_status()
            print(f"<-- [SUCCESS TWILIO] Pesan terkirim! SID: {response.json().get('sid')}", flush=True)
    except Exception as e:
        print(f"!!! [ERROR TWILIO] Gagal mengirim pesan: {e}", flush=True)

async def process_and_reply_twilio_v2(from_number: str, user_message: str):
    """Proses pesan WA menggunakan pendekatan V2 (Inject Semua Data) melalui Twilio"""
    print(f"--> [PROCESS TWILIO V2] Memulai proses untuk {from_number}...", flush=True)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://llmproject-production.up.railway.app/api/v2/items/ask",
                json={"question": user_message},
                timeout= None
            )
            response.raise_for_status()
            answer_text = response.json().get("answer", "Maaf, AI tidak mengembalikan jawaban.")
            print(f"<-- [PROCESS V2] Respon AI diterima: '{answer_text[:80]}...'", flush=True)
    except Exception as e:
        answer_text = f"Maaf, sistem V2 sedang mengalami gangguan: {str(e)}"
        print(f"!!! [ERROR TWILIO V2] Terjadi kesalahan: {e}", flush=True)
        
    await send_twilio_message(from_number, answer_text)

async def process_and_reply_twilio_v3(from_number: str, user_message: str):
    """Proses pesan WA menggunakan pendekatan V3 (LangGraph Agent) melalui Twilio"""
    print(f"--> [PROCESS TWILIO V3] Memulai proses untuk {from_number}...", flush=True)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://llmproject-production.up.railway.app/api/v3/agent/ask",
                json={"question": user_message},
                timeout= None
            )
            response.raise_for_status()
            answer_text = response.json().get("answer", "Maaf, AI tidak mengembalikan jawaban.")
            print(f"<-- [PROCESS V3] Respon AI diterima: '{answer_text[:80]}...'", flush=True)
    except Exception as e:
        answer_text = f"Maaf, sistem V3 sedang mengalami gangguan: {str(e)}"
        print(f"!!! [ERROR TWILIO V3] Terjadi kesalahan: {e}", flush=True)
        
    await send_twilio_message(from_number, answer_text)

@router.post("/v2/webhook")
async def receive_twilio_v2(request: Request, background_tasks: BackgroundTasks):
    """Endpoint Webhook V2 khusus untuk Twilio (menggunakan format Form-Data)"""
    form_data = await request.form()
    from_number = form_data.get("From")
    body = form_data.get("Body")
    
    if from_number and body:
        print(f"\n[RECEIVE TWILIO V2] Pesan diterima dari {from_number}: '{body}'", flush=True)
        background_tasks.add_task(process_and_reply_twilio_v2, from_number, body)
        
    return Response(content="<Response></Response>", media_type="application/xml")

@router.post("/v3/webhook")
async def receive_twilio_v3(request: Request, background_tasks: BackgroundTasks):
    """Endpoint Webhook V3 khusus untuk Twilio (menggunakan format Form-Data)"""
    form_data = await request.form()
    from_number = form_data.get("From")
    body = form_data.get("Body")
    
    if from_number and body:
        print(f"\n[RECEIVE TWILIO V3] Pesan diterima dari {from_number}: '{body}'", flush=True)
        background_tasks.add_task(process_and_reply_twilio_v3, from_number, body)
        
    return Response(content="<Response></Response>", media_type="application/xml")