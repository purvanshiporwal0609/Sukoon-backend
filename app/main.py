from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Sukoon - Mental Wellness Chatbot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sukoon-sable.vercel.app",  # your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running and reachable"}

@app.get("/")
async def root():
    return {"message": "Welcome to Sukoon API. Use /api/chat for wellness support."}