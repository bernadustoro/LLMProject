import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.database import SessionLocal
from app.services.item_service import item_service
from app.services.user_service import user_service

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

router = APIRouter()

# ==========================================
# 1. Definisi Tools (Alat untuk Agent)
# ==========================================
@tool
def cari_data_produk() -> str:
    """Gunakan fungsi ini HANYA jika pertanyaan berkaitan dengan produk, barang, atau harga yang ada di database."""
    print("\n=== DEBUG V3: TOOL 'cari_data_produk' DIPANGGIL ===", flush=True)
    print("Agent memutuskan untuk melakukan query ke database tabel items...", flush=True)
    db = SessionLocal()
    try:
        # Menggunakan service layer yang sama dengan endpoint /api/v1/items
        items = item_service.get_items(db)
        print(f"Berhasil menarik {len(items)} produk dari database.\n", flush=True)
        items_data = [{
            "name": i.name, 
            "description": i.description, 
            "price": i.price, 
            "is_offer": i.is_offer
        } for i in items]
        return json.dumps(items_data)
    except Exception as e:
        return str(e)
    finally:
        db.close()

@tool
def cari_data_pelanggan() -> str:
    """Gunakan fungsi ini HANYA jika pertanyaan berkaitan dengan pengguna, user, pelanggan, atau akun."""
    print("\n=== DEBUG V3: TOOL 'cari_data_pelanggan' DIPANGGIL ===", flush=True)
    print("Agent memutuskan untuk melakukan query ke database tabel users...", flush=True)
    db = SessionLocal()
    try:
        # Menggunakan service layer yang sama dengan endpoint /api/v1/users
        users = user_service.get_users(db)
        print(f"Berhasil menarik {len(users)} pengguna dari database.\n", flush=True)
        users_data = [{
            "username": u.username, 
            "email": u.email, 
            "full_name": u.full_name, 
            "is_active": u.is_active
        } for u in users]
        return json.dumps(users_data)
    except Exception as e:
        return str(e)
    finally:
        db.close()

tools = [cari_data_produk, cari_data_pelanggan]

# ==========================================
# 2. Setup LLM & Agent Executor
# ==========================================
# Pastikan variabel environment GEMINI_API_KEY sudah terbaca
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.3)

system_prompt = "Kamu adalah asisten AI toko cerdas. Gunakan alat (tools) yang tersedia untuk mencari informasi di database sebelum menjawab. Jawab dengan bahasa Indonesia yang ramah dan ringkas."

# Membuat Agent menggunakan LangGraph (standar terbaru LangChain)
agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str

@router.post("/ask", response_model=AskResponse)
async def ask_agent_v3(request: AskRequest):
    try:
        print(f"\n=== DEBUG V3: ENDPOINT /ask DIPANGGIL ===", flush=True)
        print(f"Pertanyaan user: '{request.question}'", flush=True)
        print("Agent mulai berpikir... (Belum ada query ke DB yang dijalankan)\n", flush=True)
        
        # Agent akan berpikir dan memilih tool secara otomatis
        response = agent_executor.invoke({"messages": [("user", request.question)]})
        
        # Mengekstrak konten jawaban (Bisa berupa string atau list of dict)
        content = response["messages"][-1].content
        if isinstance(content, list):
            answer_text = "".join([part.get("text", "") for part in content if isinstance(part, dict)])
        else:
            answer_text = str(content)
            
        return {"question": request.question, "answer": answer_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))