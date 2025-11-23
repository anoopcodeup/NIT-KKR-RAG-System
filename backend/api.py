from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from rag_system import RAGSystem
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NIT KKR RAG API",
    description="RESTful API for NIT Kurukshetra RAG System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_system: Optional[RAGSystem] = None

def get_rag_system() -> RAGSystem:
    """Get or initialize the RAG system."""
    global rag_system
    if rag_system is None:
        try:
            if not Config.validate_groq_config():
                use_groq = False
            else:
                use_groq = True
            rag_system = RAGSystem(use_groq=use_groq)
            logger.info("RAG system initialized successfully")
        except FileNotFoundError as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise HTTPException(
                status_code=503,
                detail="RAG system not available. Please ensure vector store is set up."
            )
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize RAG system: {str(e)}"
            )
    return rag_system

class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 5

class Source(BaseModel):
    title: str
    url: str
    score: float
    score_type: str
    content_preview: str

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Source]
    num_sources: int

class StatsResponse(BaseModel):
    total_chunks: int
    unique_documents: int
    total_words: int
    average_chunk_length: float
    model_name: str
    embedding_dimension: int
    groq_enabled: bool
    groq_model: Optional[str]
    groq_available: bool
    reranker_enabled: bool

class HealthResponse(BaseModel):
    status: str
    message: str
    rag_system_ready: bool

@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "NIT KKR RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "query": "/api/query",
            "stats": "/api/stats"
        }
    }

@app.get("/api/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    try:
        rag = get_rag_system()
        return HealthResponse(
            status="healthy",
            message="RAG system is ready",
            rag_system_ready=True
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            message=f"RAG system not available: {str(e)}",
            rag_system_ready=False
        )

@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def query(request: QueryRequest):
    """
    Query the RAG system with a question.
    
    Args:
        request: Query request with question and optional k parameter
    
    Returns:
        Query response with answer and sources
    """
    try:
        rag = get_rag_system()
        
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = rag.answer_query(request.query, k=request.k or 5)
        
        sources = [
            Source(
                title=s.get("title", "Unknown"),
                url=s.get("url", "Unknown"),
                score=s.get("score", 0.0),
                score_type=s.get("score_type", "similarity"),
                content_preview=s.get("content_preview", "")
            )
            for s in result.get("sources", [])
        ]
        
        return QueryResponse(
            query=result.get("query", request.query),
            response=result.get("response", "No response generated"),
            sources=sources,
            num_sources=result.get("num_sources", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/api/stats", response_model=StatsResponse, tags=["RAG"])
async def get_stats():
    """Get system statistics."""
    try:
        rag = get_rag_system()
        stats = rag.get_system_stats()
        
        return StatsResponse(
            total_chunks=stats.get("total_chunks", 0),
            unique_documents=stats.get("unique_documents", 0),
            total_words=stats.get("total_words", 0),
            average_chunk_length=stats.get("average_chunk_length", 0.0),
            model_name=stats.get("model_name", "unknown"),
            embedding_dimension=stats.get("embedding_dimension", 0),
            groq_enabled=stats.get("groq_enabled", False),
            groq_model=stats.get("groq_model"),
            groq_available=stats.get("groq_available", False),
            reranker_enabled=stats.get("reranker_enabled", False)
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

