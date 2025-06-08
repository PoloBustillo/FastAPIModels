# main.py
from fastapi import File, UploadFile, FastAPI, HTTPException
import shutil
import os
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Mi API FastAPI",
    description="API de ejemplo con Docker y GitHub Actions",
    version="1.0.0"
)
2

# Modelo de datos
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

# Base de datos simulada
items_db = [
    {"id": 1, "name": "Laptop", "description": "Laptop gaming", "price": 1200.00, "is_active": True},
    {"id": 2, "name": "Mouse", "description": "Mouse inalámbrico", "price": 25.99, "is_active": True}
]

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

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    new_id = max([i["id"] for i in items_db]) + 1 if items_db else 1
    item_dict = item.dict()
    item_dict["id"] = new_id
    items_db.append(item_dict)
    return item_dict

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    for i, existing_item in enumerate(items_db):
        if existing_item["id"] == item_id:
            item_dict = item.dict()
            item_dict["id"] = item_id
            items_db[i] = item_dict
            return item_dict
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            del items_db[i]
            return {"message": "Item eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Item no encontrado")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)