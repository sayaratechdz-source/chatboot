from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Vehicule(Base):
    __tablename__ = "vehicules"
    
    id = Column(Integer, primary_key=True, index=True)
    marque = Column(String, index=True)
    modele = Column(String, index=True)
    annee = Column(Integer)
    immatriculation = Column(String, unique=True, index=True)
    
    pieces = relationship("Piece", back_populates="vehicule_compatible")

class Piece(Base):
    __tablename__ = "pieces"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    reference = Column(String, unique=True, index=True)
    description = Column(String)
    prix = Column(Float)
    stock = Column(Integer, default=0)
    vehicule_id = Column(Integer, ForeignKey("vehicules.id"), nullable=True)
    
    vehicule_compatible = relationship("Vehicule", back_populates="pieces")

class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    telephone = Column(String)
    adresse = Column(String)
    ville = Column(String)
    specialite = Column(String)  # ex: "Freinage, Moteur"

class Garage(Base):
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    telephone = Column(String)
    adresse = Column(String)
    ville = Column(String)
    specialite = Column(String)  # ex: "Mécanique générale, Électricité"

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    email = Column(String, unique=True, index=True)
    telephone = Column(String)
    
    commandes = relationship("Commande", back_populates="client")

class Commande(Base):
    __tablename__ = "commandes"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    date_commande = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default="en_attente")
    total = Column(Float)
    
    client = relationship("Client", back_populates="commandes")
    items = relationship("CommandeItem", back_populates="commande")

class CommandeItem(Base):
    __tablename__ = "commande_items"
    
    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id"))
    piece_id = Column(Integer, ForeignKey("pieces.id"))
    quantite = Column(Integer, default=1)
    prix_unitaire = Column(Float)
    
    commande = relationship("Commande", back_populates="items")
    piece = relationship("Piece")
