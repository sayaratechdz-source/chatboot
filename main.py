from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, Response
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
from seed_data import seed_database

# Création des tables et initialisation des données au démarrage
models.Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="AutoChatbot - API",
    version="1.0",
    description="API du chatbot automobile intelligent pour la wilaya de Oum El Bouaghi."
)

# CORS - permet à l'app mobile et au navigateur d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# MODÈLES DE REQUÊTE
# =======================

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

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat IA"])
async def chat_endpoint(req: ChatRequest):
    """Envoie un message au chatbot et reçoit une réponse."""
    try:
        reply, tools = await process_message(
            req.message, req.session_id, req.image_b64, req.media_type
        )
        return ChatResponse(response=reply, tools_used=tools)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream", tags=["Chat IA"])
async def chat_stream_endpoint(req: ChatRequest):
    """Endpoint streaming SSE - envoie la réponse caractère par caractère."""
    async def generate():
        try:
            reply, tools = await process_message(
                req.message, req.session_id, req.image_b64, req.media_type
            )
            for char in reply:
                data = json.dumps({"char": char, "done": False})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.018)
            yield f"data: {json.dumps({'char': '', 'done': True, 'tools': tools})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# =======================
# ROUTES PIÈCES
# =======================

@app.get("/api/pieces", response_model=List[schemas.PieceResponse], tags=["Pièces"])
def read_pieces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des pièces disponibles."""
    return crud.get_pieces(db, skip=skip, limit=limit)


@app.post("/api/pieces", response_model=schemas.PieceResponse, tags=["Pièces"])
def create_piece(piece: schemas.PieceCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle pièce."""
    db_piece = crud.get_piece_by_reference(db, reference=piece.reference)
    if db_piece:
        raise HTTPException(status_code=400, detail="Une pièce avec cette référence existe déjà")
    return crud.create_piece(db=db, piece=piece)


@app.get("/api/pieces/search", response_model=List[schemas.PieceResponse], tags=["Pièces"])
def search_pieces(nom: str, db: Session = Depends(get_db)):
    """Recherche des pièces par nom."""
    return crud.get_pieces_by_nom(db, nom=nom)

# =======================
# ROUTES VÉHICULES
# =======================

@app.get("/api/vehicules", response_model=List[schemas.VehiculeResponse], tags=["Véhicules"])
def read_vehicules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des véhicules."""
    return crud.get_vehicules(db, skip=skip, limit=limit)


@app.post("/api/vehicules", response_model=schemas.VehiculeResponse, tags=["Véhicules"])
def create_vehicule(vehicule: schemas.VehiculeCreate, db: Session = Depends(get_db)):
    """Enregistre un nouveau véhicule."""
    db_vehicule = crud.get_vehicule_by_immatriculation(db, immatriculation=vehicule.immatriculation)
    if db_vehicule:
        raise HTTPException(status_code=400, detail="Ce véhicule est déjà enregistré")
    return crud.create_vehicule(db=db, vehicule=vehicule)

# =======================
# ROUTES COMMANDES
# =======================

@app.get("/api/commandes", response_model=List[schemas.CommandeResponse], tags=["Commandes"])
def read_commandes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des commandes."""
    return crud.get_commandes(db, skip=skip, limit=limit)

# =======================
# MONITORING & UI
# =======================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Vérifie que le serveur fonctionne."""
    import os
    key = os.environ.get("GROQ_API_KEY", "")
    return {
        "status": "ok",
        "groq_key_set": bool(key),
        "groq_key_prefix": key[:8] + "..." if len(key) > 8 else "EMPTY"
    }


@app.get("/", tags=["Monitoring"])
async def read_root():
    """Sert la page HTML du chatbot."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>AutoChatbot API</h1><p>Go to <a href='/docs'>/docs</a> for API documentation.</p>"
        )
