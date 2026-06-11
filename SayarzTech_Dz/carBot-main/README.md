# 🚗 CarBot — Assistant Automobile IA

> Chatbot intelligent spécialisé en mécanique automobile pour la wilaya de **Oum El Bouaghi**, Algérie.
> Propulsé par **Claude AI (Anthropic)** + **FastAPI** + **SQLite**.

---

## 👥 Auteurs

| Nom | Rôle |
|-----|------|
| **Benaboud Roqia** | — Assistant IA |
| **Abdrhmane Aref** | Développeur — Frontend, UI/UX, Intégration,backend |
| **ABBA** |  — Architecture, Logique métier, Outils |

---

## ⚠️ Clé API Claude requise

> **Ce projet nécessite une clé API Anthropic (Claude) pour fonctionner.**

1 🏪 **Garages & Mécaniciens** — Trouve les ateliers à Aïn Mlila, Oum El Bouaghi, Aïn Beïda, Aïn Fakroun
- 💰 **Prix & Stock** — Vérifie la disponibilité et les prix des pièces en DZD
- 📋 **Devis automatique** — Génère un devis pièces + main d'œuvre
- 📄 **Facture PDF** — Facture professionnelle avec signature électronique et TVA
- 🎙️ **Reconnaissance vocale** — Parle directement à Abdou
- 🔊 **Synthèse vocale** — Abdou peut lire ses réponses à voix haute
- 🌙 **Mode nuit** — Interface sombre confortable
- 📱 **Responsive** — Fonctionne sur mobile et desktop
- 🧠 **Intelligence émotionnelle** — Comprend les salutations, remerciements, émotions
- 📷 **Analyse d'image** — Envoie une photo de ta panne, Abdou l'analyse

---

## 🗺️ Zone couverte

**Wilaya de Oum El Bouaghi (04)**
- Aïn Mlila
- Oum El Bouaghi
- Aïn Beïda
- Aïn Fakroun

**Base de données locale:**
- 53 pièces automobiles
- 15 véhicules compatibles
- 13 fournisseurs
- 23 garages & mécaniciens

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+ / FastAPI |
| IA | Anthropic Claude (claude-haiku) |
| Base de données | SQLite + SQLAlchemy |
| Frontend | HTML5 / CSS3 / JavaScript vanilla |
| Mobile | React Native (Expo) |

---

## 🚀 Installation & Lancement

### Prérequis
- Python 3.11+
- Clé API Anthropic

### 1. Cloner le projet
```bash
git clone https://github.com/benaboud-roqia/AutoChatbot.git
cd AutoChatbot
```

### 2. Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env et ajouter ta clé API Anthropic
```

Contenu du `.env`:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
CLAUDE_MODEL=claude-haiku-4-5-20251001
DATABASE_URL=sqlite:///./chatbot_auto.db
```

### 4. Initialiser la base de données
```bash
python seed_data.py
```

### 5. Lancer le serveur
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Ouvrir dans le navigateur
```
http://localhost:8000
```

---

## 📁 Structure du projet

```
AutoChatbot/
├── backend/
│   ├── main.py          # API FastAPI — routes et endpoints
│   ├── agent.py         # Logique IA — Abdou, outils, process_message
│   ├── models.py        # Modèles SQLAlchemy (Garage, Piece, Fournisseur...)
│   ├── schemas.py       # Schémas Pydantic
│   ├── crud.py          # Opérations base de données
│   ├── database.py      # Configuration SQLite
│   ├── seed_data.py     # Données initiales (garages, pièces, fournisseurs)
│   ├── index.html       # Interface web du chatbot
│   ├── requirements.txt # Dépendances Python
│   └── .env.example     # Template variables d'environnement
├── AutoChatbot/         # App mobile React Native (Expo)
│   ├── App.js
│   └── package.json
└── README.md
```

---

## 🤖 Outils d'Abdou

| Outil | Description |
|-------|-------------|
| `diagnostic` | Analyse les symptômes de panne |
| `identification_pieces` | Identifie une pièce par nom/modèle |
| `prix_stock` | Prix et disponibilité d'une pièce |
| `commandes` | Prépare une commande de pièces |
| `trouver_garage` | Trouve un garage dans la wilaya |
| `trouver_fournisseur` | Trouve un fournisseur de pièces |
| `entretien_vehicule` | Programme d'entretien par kilométrage |
| `main_oeuvre` | Estimation coût main d'œuvre en DZD |
| `checklist_occasion` | Checklist achat voiture d'occasion |
| `rappel_entretien` | Calcule la prochaine vidange |
| `urgence_panne` | Conseils urgents en cas de panne grave |

---

## 💬 Exemples d'utilisation

```
"salam" → Abdou répond chaleureusement en darija
"garage a ain beida" → Liste les 5 garages d'Aïn Beïda avec téléphones
"ma Dacia Logan fait un bruit en freinant" → Diagnostic + conseils
"prix plaquettes de frein Symbol" → Prix en DZD + stock
"prochaine vidange à 87000 km" → Calcul automatique
"je veux acheter une voiture d'occasion" → Checklist complète
```

---

## 📸 Interface

- Header pastel gradient avec logo CarBot
- Sidebar historique des conversations
- Mode sombre / clair
- Sélecteur de langue (Auto / FR / AR darija)
- Bouton microphone pour la voix
- Analyse d'images (photos de pannes)
- Système de factures PDF avec signature électronique

---

## 📄 Licence

Projet académique — Wilaya de Oum El Bouaghi, Algérie.  
© 2025 Benaboud Roqia, Abdrhmane Aref, ABBA

---

*"Abdou est là pour toi, que tu sois à Aïn Mlila, Oum El Bouaghi, Aïn Beïda ou Aïn Fakroun."* 🔧
