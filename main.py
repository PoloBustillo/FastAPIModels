# main.py
from fastapi import File, UploadFile, FastAPI, HTTPException, Query
import shutil
import os
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPModel, CLIPProcessor
from PIL import Image
import pandas as pd



UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Mi API FastAPI",
    description="API de ejemplo con Docker y GitHub Actions",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "¡Hola! API FastAPI funcionando correctamente"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/image-to-text")
async def upload_image(file: UploadFile = File(...)):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    img = Image.open(file.file).convert("RGB")
    inputs = processor(img, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    # file_location = os.path.join(UPLOAD_DIR, file.filename)
    # with open(file_location, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    return {
        "filename": file.filename,
        "caption": caption,
        "message": "Image uploaded and caption generated successfully"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)