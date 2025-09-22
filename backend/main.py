import os
import tempfile
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from pdf_processor import build_retriever_from_pdf_bytes
from rag_chain import build_rag_chain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API Key Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDsvpw5fYQnVFtm8Q4Ksd8g1AqUEBsGSdg")
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    logger.info("Google API key configured")
else:
    logger.warning("No Google API key found. Please set GOOGLE_API_KEY environment variable.")

app = FastAPI(title="PDF Chat API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the retriever (in production, use a proper database)
retriever_store: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    question: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str

@app.get("/")
async def root():
    return {"message": "PDF Chat API is running!"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Form("default")):
    """Upload and process a PDF file"""
    logger.info(f"Upload request received for session: {session_id}, filename: {file.filename}")
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size (limit to 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        # Read the uploaded file with timeout
        pdf_bytes = await asyncio.wait_for(file.read(), timeout=30.0)
        
        if len(pdf_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file received.")
        
        logger.info(f"PDF file size: {len(pdf_bytes)} bytes")
        
        # Process the PDF and create retriever with timeout
        retriever = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, build_retriever_from_pdf_bytes, pdf_bytes
            ),
            timeout=60.0  # 60 second timeout for PDF processing
        )
        
        # Store the retriever for this session
        retriever_store[session_id] = retriever
        logger.info(f"Retriever stored for session: {session_id}")
        logger.info(f"Available sessions: {list(retriever_store.keys())}")
        
        return {
            "message": "PDF processed successfully!",
            "session_id": session_id,
            "filename": file.filename,
            "file_size": len(pdf_bytes)
        }
    except asyncio.TimeoutError:
        logger.error(f"Timeout processing PDF for session: {session_id}")
        raise HTTPException(status_code=408, detail="Request timeout. The PDF is too large or complex to process.")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the uploaded PDF"""
    logger.info(f"Chat request received for session: {request.session_id}")
    logger.info(f"Available sessions: {list(retriever_store.keys())}")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    if request.session_id not in retriever_store:
        raise HTTPException(status_code=404, detail="No PDF uploaded for this session. Please upload a PDF first.")
    
    try:
        retriever = retriever_store[request.session_id]
        chain = build_rag_chain(retriever)
        
        # Add timeout for chat response
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, chain.invoke, request.question
            ),
            timeout=30.0  # 30 second timeout for chat response
        )
        
        logger.info(f"Chat response generated for session: {request.session_id}")
        return ChatResponse(
            answer=response,
            session_id=request.session_id
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout generating chat response for session: {request.session_id}")
        raise HTTPException(status_code=408, detail="Request timeout. The AI is taking too long to respond.")
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(retriever_store),
        "api_key_configured": bool(GOOGLE_API_KEY)
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    if session_id in retriever_store:
        del retriever_store[session_id]
        logger.info(f"Session {session_id} cleared")
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/sessions")
async def clear_all_sessions():
    """Clear all sessions"""
    count = len(retriever_store)
    retriever_store.clear()
    logger.info(f"All {count} sessions cleared")
    return {"message": f"All {count} sessions cleared successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
