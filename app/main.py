from dotenv import load_dotenv
from fastapi import FastAPI,Request,status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exception.exceptionCustom import CustomException
from app.db.database import Base, engine
from app.api.endpoints import items
from app.api.endpoints import users
from app.api.endpoints import items_v2
from app.api.endpoints import items_v3
from app.api.endpoints import whatsapp

# Load variabel lingkungan dari file .env (misal: GEMINI_API_KEY)
load_dotenv()

# Baris ini akan membuat tabel di database jika belum ada.
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status,
            "code": exc.status_code,
            "message": exc.message
        }
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Ubah detail error Pydantic menjadi list string yang lebih mudah dibaca
    errors = exc.errors()
    # Kita bisa memformat error agar lebih mudah dibaca oleh frontend
    error_messages = []
    for err in errors:
        # err["loc"] biasanya berisi ["body", "nama_field"]
        field = err["loc"][-1] if len(err["loc"]) > 1 else "unknown field"
        message = err["msg"]
        error_messages.append(f"Error pada field '{field}': {message}")
    
    # Gabungkan semua pesan error jika ada lebih dari satu
    formatted_message = " | ".join(error_messages)

    # Kembalikan response sesuai format custom kamu
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, # Atau 422, tergantung preferensi
        content={
            "status": "error",
            "code": status.HTTP_400_BAD_REQUEST,
            "message": f"Validasi data gagal. {formatted_message}"
        }
    )
    
# Sertakan router dari modul items
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Sertakan router v2 untuk fitur AI/LLM
app.include_router(items_v2.router, prefix="/api/v2/items", tags=["items-v2-llm"])
app.include_router(items_v3.router, prefix="/api/v3/agent", tags=["agent-v3-langchain"])

# Sertakan router WhatsApp
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp-bot"])
