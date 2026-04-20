import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.db.database import get_db

router = APIRouter()

jenis_model = 'gemini-2.5-flash-lite'  # Atau 'gemini-2.0-flash' sesuai kebutuhan Anda
# Inisialisasi model menggunakan LangChain (Otomatis membaca GEMINI_API_KEY dari .env)
model = ChatGoogleGenerativeAI(model=jenis_model, temperature=0.3)

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_gemini_about_items(request: AskRequest, db: Session = Depends(get_db)):
    try:
        # Mengambil data produk langsung dari tabel 'items' di database.
        # Jika nama tabel Anda berbeda, ubah kata 'items' di bawah ini.
        result_items = db.execute(text("SELECT name, description, price, is_offer FROM items")).mappings().all()
        result_users = db.execute(text("SELECT username, email, full_name, is_active FROM users")).mappings().all()
        
        # Mengubah hasil query database menjadi list of dictionary
        items_list = [dict(row) for row in result_items]
        users_list = [dict(row) for row in result_users]
        
        # Gabungkan data produk dan pengguna untuk konteks yang lebih kaya
        context_data = {
            "items": items_list,
            "users": users_list
        }
        
        # Konversi ke JSON dengan indentasi untuk keterbacaan
        context_data = json.dumps(context_data, indent=2)
        
        # Cetak ke terminal server untuk membuktikan query selalu ditarik
        print("\n=== DEBUG V2: BUKTI QUERY SELALU JALAN ===", flush=True)
        print(f"Berhasil menarik {len(items_list)} produk dan {len(users_list)} pelanggan.", flush=True)
        print(f"Menyisipkan {len(context_data)} karakter teks JSON ke dalam Prompt LLM...\n", flush=True)

        # Merakit Prompt Engineering
        prompt = f"""
        Kamu adalah asisten AI toko cerdas. 
        Berikut adalah data produk terbaru kami saat ini dalam format JSON:
        
        {context_data}
        
        Berdasarkan data produk di atas, tolong jawab pertanyaan berikut:
        "{request.question}"
        
        Aturan:
        - Jawab dengan ramah dan ringkas.
        - Pahami maksud pelanggan meskipun ada typo atau penyingkatan (contoh: "7juta" berarti 7000000).
        - Jika pelanggan mencari harga tertentu dan tidak ada yang pas, tawarkan produk dengan harga yang paling mendekati.
        """
        
        # Eksekusi prompt dengan LangChain
        response = model.invoke(prompt)
        return {"question": request.question, "answer": response.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/model")
async def update_model(new_model_name: str):
    global model
    try:
        model = ChatGoogleGenerativeAI(model=new_model_name, temperature=0.3)
        return {"message": f"Model updated to {new_model_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))