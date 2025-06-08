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
import joblib

# Cargar el pipeline y el LabelEncoder
pipeline_prod = joblib.load('./modelos/modelo_confiabilidad_usuario_biblioteca.pkl')
le_prod = joblib.load('./modelos/label_encoder_tipo_usuario.pkl')
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Mi API FastAPI",
    description="API de ejemplo con Docker y GitHub Actions",
    version="1.0.0"
)
# 1️⃣ Carga del modelo CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")


# Modelo de entrada
class Usuario(BaseModel):
    libros_a_tiempo: int
    libros_tarde: int
    total_prestamos: int
    multas_pagadas: int
    tipo_usuario: str  # estudiante, profesor, externo
    antiguedad_meses: int
    historial_pagos: float
    sanciones: int
    participacion_eventos: int


# Endpoint para predecir confiabilidad
@app.post("/predecir_confiabilidad")
def predecir_confiabilidad(usuario: Usuario):
    try:
        # Convertir tipo_usuario a número
        tipo_usuario_num = le_prod.transform([usuario.tipo_usuario])[0]

        # Crear DataFrame de entrada
        df_usuario = pd.DataFrame([{
            'libros_a_tiempo': usuario.libros_a_tiempo,
            'libros_tarde': usuario.libros_tarde,
            'total_prestamos': usuario.total_prestamos,
            'multas_pagadas': usuario.multas_pagadas,
            'tipo_usuario': tipo_usuario_num,
            'antiguedad_meses': usuario.antiguedad_meses,
            'historial_pagos': usuario.historial_pagos,
            'sanciones': usuario.sanciones,
            'participacion_eventos': usuario.participacion_eventos
        }])

        # Predecir
        porcentaje_confiabilidad = pipeline_prod.predict_proba(df_usuario)[:, 1][0] * 100

        return {
            "porcentaje_confiabilidad": round(porcentaje_confiabilidad, 2)
        }

    except Exception as e:
        return {"error": str(e)}
@app.post("/zero-shot")
async def zero_shot_classify(
    file: UploadFile = File(...),
    labels: list[str] = Query([
        "una pintura renacentista", "una escultura moderna", "una obra abstracta",
        "óleo sobre lienzo", "acuarela", "témpera", "fresco", "pintura mural", "pintura al temple", "pintura al pastel",
        "pintura digital", "pintura impresionista", "pintura expresionista"
    ])
):
    # Lee imagen
    img = Image.open(file.file).convert("RGB")
    # Preprocesamiento
    inputs = processor(text=labels, images=img, return_tensors="pt", padding=True)
    # Inference
    outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]
    results = {label: float(prob) for label, prob in zip(labels, probs)}
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:3]
    return {"predictions": dict(sorted_results)}

@app.post("/embeddings/image")
async def get_image_embedding(file: UploadFile = File(...)):
    img = Image.open(file.file).convert("RGB")
    img_input = processor(images=img, return_tensors="pt")
    feats = model.get_image_features(**img_input)
    norm = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return {"embedding": norm[0].tolist()}

@app.post("/embeddings/text")
async def get_text_embedding(texts: list[str]):
    txt_input = processor(text=texts, return_tensors="pt", padding=True)
    feats = model.get_text_features(**txt_input)
    norm = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return {"embeddings": [v.tolist() for v in norm]}

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