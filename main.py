# main.py
from fastapi import FastAPI

app = FastAPI(
    title="AI API Skeleton",
    description="Minimal FastAPI skeleton for AI APIs",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to your AI API skeleton!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
