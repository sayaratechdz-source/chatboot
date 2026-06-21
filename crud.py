from sqlalchemy.orm import Session
from models import Piece, Vehicule, Client, Commande, CommandeItem
from typing import List, Optional

# ==================== PIECES ====================

def get_pieces(db: Session, skip: int = 0, limit: int = 100) -> List[Piece]:
    return db.query(Piece).offset(skip).limit(limit).all()

def get_piece_by_reference(db: Session, reference: str) -> Optional[Piece]:
    return db.query(Piece).filter(Piece.reference == reference).first()

def get_pieces_by_nom(db: Session, nom: str) -> List[Piece]:
    return db.query(Piece).filter(Piece.nom.ilike(f"%{nom}%")).all()

def create_piece(db: Session, piece) -> Piece:
    db_piece = Piece(
        nom=piece.nom,
        reference=piece.reference,
        description=piece.description,
        prix=piece.prix,
        stock=piece.stock,
        categorie=getattr(piece, "categorie", None),
    )
    db.add(db_piece)
    db.commit()
    db.refresh(db_piece)
    return db_piece

# ==================== VEHICULES ====================

def get_vehicules(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicule]:
    return db.query(Vehicule).offset(skip).limit(limit).all()

def get_vehicule_by_immatriculation(db: Session, immatriculation: str) -> Optional[Vehicule]:
    return db.query(Vehicule).filter(Vehicule.immatriculation == immatriculation).first()

def create_vehicule(db: Session, vehicule) -> Vehicule:
    db_vehicule = Vehicule(
        immatriculation=vehicule.immatriculation,
        marque=vehicule.marque,
        modele=vehicule.modele,
        annee=vehicule.annee,
    )
    db.add(db_vehicule)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule

# ==================== CLIENTS ====================

def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    return db.query(Client).filter(Client.email == email).first()

def create_client(db: Session, nom: str, email: str, telephone: Optional[str] = None) -> Client:
    client = Client(nom=nom, email=email, telephone=telephone)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

# ==================== COMMANDES ====================

def get_commandes(db: Session, skip: int = 0, limit: int = 100) -> List[Commande]:
    return db.query(Commande).offset(skip).limit(limit).all()

def create_commande(db: Session, client_id: Optional[int], pieces: List[dict],
                    session_id: Optional[str] = None, vehicule_id: Optional[int] = None) -> Commande:
    commande = Commande(
        client_id=client_id,
        session_id=session_id,
        vehicule_id=vehicule_id,
        total=0.0
    )
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
