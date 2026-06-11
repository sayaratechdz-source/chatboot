from sqlalchemy.orm import Session
from models import Piece, Vehicule, Client, Commande, CommandeItem
from typing import List, Optional

def get_pieces(db: Session, skip: int = 0, limit: int = 100) -> List[Piece]:
    return db.query(Piece).offset(skip).limit(limit).all()

def get_piece_by_reference(db: Session, reference: str) -> Optional[Piece]:
    return db.query(Piece).filter(Piece.reference == reference).first()

def get_pieces_by_nom(db: Session, nom: str) -> List[Piece]:
    return db.query(Piece).filter(Piece.nom.ilike(f"%{nom}%")).all()

def get_vehicules(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicule]:
    return db.query(Vehicule).offset(skip).limit(limit).all()

def create_client(db: Session, nom: str, email: str, telephone: Optional[str] = None) -> Client:
    client = Client(nom=nom, email=email, telephone=telephone)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

def create_commande(db: Session, client_id: int, pieces: List[dict]) -> Commande:
    commande = Commande(client_id=client_id, total=0.0)
    db.add(commande)
    db.flush()
    
    total = 0.0
    for item in pieces:
        piece = db.query(Piece).filter(Piece.id == item["piece_id"]).first()
        if piece:
            commande_item = CommandeItem(
                commande_id=commande.id,
                piece_id=piece.id,
                quantite=item.get("quantite", 1),
                prix_unitaire=piece.prix
            )
            db.add(commande_item)
            total += piece.prix * item.get("quantite", 1)
    
    commande.total = total
    db.commit()
    db.refresh(commande)
    return commande
