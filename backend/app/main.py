"""
FastAPI application for Musical Instrument Manual Q&A System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Musical Instrument Manual Q&A API",
    description="RAG-powered Q&A system for musical instrument manuals",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative React dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes (will be created next)
from app.api.routes import manuals, qa, stats

# Register routes
app.include_router(manuals.router, prefix="/api/manuals", tags=["manuals"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])
app.include_router(stats.router, prefix="/api", tags=["stats"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Musical Instrument Manual Q&A API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if OpenAI API key is configured
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))

    return {
        "status": "healthy",
        "openai_configured": openai_configured,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
