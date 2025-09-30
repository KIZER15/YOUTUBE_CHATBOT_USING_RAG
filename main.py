# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_utils import run_rag

# Create FastAPI app
app = FastAPI(title="YouTube RAG Chatbot")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],        # Allow all headers
)

# Request model
class RAGRequest(BaseModel):
    video_id: str
    question: str

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to YouTube RAG Chatbot API"}

# RAG endpoint
@app.post("/chat")
def chat(request: RAGRequest):
    try:
        # Call your RAG utility
        answer = run_rag(request.video_id, request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
