from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Import Agentic System components
from agentic_system.workflows.agentic_rag import create_agentic_rag_workflow
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NITK-Agent API",
    description="Agentic RAG API for NIT Kurukshetra Knowledge Base",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow instance
workflow = None

def get_workflow():
    """Get or initialize the Agentic RAG workflow."""
    global workflow
    if workflow is None:
        try:
            logger.info("Initializing Agentic RAG Workflow...")
            workflow = create_agentic_rag_workflow()
            logger.info("Agentic Core initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agentic Core: {e}")
            raise HTTPException(
                status_code=503,
                detail="Agentic intelligence core not available. Check API keys and configuration."
            )
    return workflow

# Models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    stream: bool = False

class Source(BaseModel):
    title: str
    url: str
    score: Optional[float] = 0.0
    content_preview: Optional[str] = ""

class AgenticMetadata(BaseModel):
    intent: str
    confidence: float
    iterations: int
    tools_used: List[str]
    execution_time: float
    quality_score: float
    reasoning: Optional[str] = ""

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Source]
    metadata: AgenticMetadata

class StatsResponse(BaseModel):
    status: str
    agents_online: int
    tools_available: List[str]
    total_queries_processed: int
    average_latency: float
    groq_model: str

@app.get("/", tags=["General"])
async def root():
    return {
        "app": "NITK-Agent API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/api/health", tags=["General"])
async def health_check():
    try:
        wf = get_workflow()
        return {"status": "healthy", "agentic_core": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/api/query", response_model=QueryResponse, tags=["Intelligence"])
async def process_query(request: QueryRequest):
    """
    Process a query through the Agentic RAG Workflow.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Empty query provided")
    
    try:
        wf = get_workflow()
        
        logger.info(f"Processing query: {request.query[:50]}...")
        result = await asyncio.to_thread(wf.invoke, {"query": request.query})
        
        # Parse sources from retrieved context or results
        # Assuming sources are provided in result['sources'] if implemented, 
        # or we extract them from result['retrieved_context']
        sources = []
        if 'sources' in result and result['sources']:
            for s in result['sources']:
                sources.append(Source(
                    title=s.get('title', 'University Resource'),
                    url=s.get('url', '#'),
                    score=s.get('score', 0.0),
                    content_preview=s.get('content_preview', '')
                ))
        
        # Build Metadata
        metadata = AgenticMetadata(
            intent=result.get('intent', 'unknown'),
            confidence=result.get('intent_classification', {}).get('confidence', 1.0) if isinstance(result.get('intent_classification'), dict) else 1.0,
            iterations=result.get('iterations', 1),
            tools_used=result.get('tools_used', []),
            execution_time=result.get('execution_time', 0.0),
            quality_score=result.get('quality_score', 0.0),
            reasoning=result.get('intent_classification', {}).get('reasoning', "") if isinstance(result.get('intent_classification'), dict) else ""
        )
        
        return QueryResponse(
            query=request.query,
            response=result.get('response', "I'm sorry, I couldn't generate a response."),
            sources=sources,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error in agentic processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=StatsResponse, tags=["Monitoring"])
async def get_system_stats():
    """Get live performance metrics of the agentic system."""
    try:
        wf = get_workflow()
        wf_stats = wf.get_workflow_stats()
        
        return StatsResponse(
            status="active",
            agents_online=4, # Router, Evaluator, Rewriter, Generator
            tools_available=wf_stats.get('tools', []),
            total_queries_processed=wf_stats.get('total_queries', 0),
            average_latency=wf_stats.get('avg_execution_time', 0.0),
            groq_model=Config.GROQ_MODEL if hasattr(Config, 'GROQ_MODEL') else os.getenv("GROQ_MODEL", "unknown")
        )
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Use standard port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

