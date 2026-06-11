from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- PIECE ---
class PieceBase(BaseModel):
    reference: str
    nom: str
    description: Optional[str] = None
    prix: float
    stock: int = 0
    categorie: Optional[str] = None

class PieceCreate(PieceBase):
    pass

class PieceResponse(PieceBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- VEHICULE ---
class VehiculeBase(BaseModel):
    immatriculation: str
    marque: str
    modele: str
    annee: int
    motorisation: Optional[str] = None

class VehiculeCreate(VehiculeBase):
    pass

class VehiculeResponse(VehiculeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- COMMANDE ---
class CommandeBase(BaseModel):
    session_id: str
    statut: str = "en_attente"

class CommandeCreate(CommandeBase):
    vehicule_id: Optional[int] = None

class CommandeResponse(CommandeBase):
    id: int
    vehicule_id: Optional[int] = None
    date_commande: datetime
    total: float

    model_config = ConfigDict(from_attributes=True)
