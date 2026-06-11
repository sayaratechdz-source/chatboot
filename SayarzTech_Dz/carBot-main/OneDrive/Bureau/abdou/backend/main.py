from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import asyncio

import models
import schemas
import crud
from database import engine, get_db
from agent import process_message

# Création des tables dans la base de données au démarrage
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gateway - Chatbot Automobile (IA Claude)", 
    version="1.0",
    description="Cette API fait office de pont entre l'application mobile et le moteur d'IA."
)

# CORS - permet à l'app mobile et au navigateur d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    image_b64: Optional[str] = None
    media_type: Optional[str] = "image/jpeg"

class ChatResponse(BaseModel):
    response: str
    tools_used: List[str]

# =======================
# ROUTES IA
# =======================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        reply, tools = await process_message(req.message, req.session_id, req.image_b64, req.media_type)
        return ChatResponse(response=reply, tools_used=tools)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """Endpoint streaming qui envoie la réponse lettre par lettre (SSE)."""
    async def generate():
        try:
            reply, tools = await process_message(req.message, req.session_id, req.image_b64, req.media_type)
            for char in reply:
                data = json.dumps({"char": char, "done": False})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.018)
            yield f"data: {json.dumps({'char': '', 'done': True, 'tools': tools})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# =======================
# ROUTES API CRUD
# =======================

@app.get("/api/pieces", response_model=List[schemas.PieceResponse], tags=["Pieces"])
def read_pieces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pieces = crud.get_pieces(db, skip=skip, limit=limit)
    return pieces

@app.post("/api/pieces", response_model=schemas.PieceResponse, tags=["Pieces"])
def create_piece(piece: schemas.PieceCreate, db: Session = Depends(get_db)):
    db_piece = crud.get_piece_by_reference(db, reference=piece.reference)
    if db_piece:
        raise HTTPException(status_code=400, detail="Une pièce avec cette référence existe déjà")
    return crud.create_piece(db=db, piece=piece)

@app.get("/api/vehicules", response_model=List[schemas.VehiculeResponse], tags=["Véhicules"])
def read_vehicules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_vehicules(db, skip=skip, limit=limit)

@app.post("/api/vehicules", response_model=schemas.VehiculeResponse, tags=["Véhicules"])
def create_vehicule(vehicule: schemas.VehiculeCreate, db: Session = Depends(get_db)):
    db_vehicule = crud.get_vehicule_by_immatriculation(db, immatriculation=vehicule.immatriculation)
    if db_vehicule:
        raise HTTPException(status_code=400, detail="Ce véhicule est déjà enregistré")
    return crud.create_vehicule(db=db, vehicule=vehicule)

# =======================
# CHECK SERVER
# =======================

@app.get("/", tags=["Monitoring"])
async def read_root():
    # Servir la page HTML du chatbot
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
