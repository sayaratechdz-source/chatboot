# 🚗 AutoChatbot — Assistant Automobile IA

> Chatbot intelligent spécialisé en mécanique automobile pour la wilaya de **Oum El Bouaghi**, Algérie.  
> Propulsé par **Claude AI (Anthropic)** + **FastAPI** + **SQLite**.

---

## 👥 Auteurs

| Nom | Rôle |
|-----|------|
| **Benaboud Roqia** | Développeuse principale — Backend, IA, Base de données |
| **Abdrhmane Aref** | Développeur — Frontend, UI/UX, Intégration |

---

## ✨ Fonctionnalités

- 🤖 **Abdou** — Mécanicien IA qui comprend le français, le darija algérien et l'arabe
- 🔧 **Diagnostic de panne** — Analyse les symptômes et propose des solutions
- 🏪 **Garages & Mécaniciens** — Trouve les ateliers à Aïn Mlila, Oum El Bouaghi, Aïn Beïda, Aïn Fakroun
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
- Aïn Mlila · Oum El Bouaghi · Aïn Beïda · Aïn Fakroun

**Base de données locale :**
- 53 pièces automobiles · 15 véhicules · 13 fournisseurs · 23 garages & mécaniciens

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+ / FastAPI |
| IA | Anthropic Claude |
| Base de données | SQLite + SQLAlchemy |
| Frontend | HTML5 / CSS3 / JavaScript |
| Mobile | React Native (Expo) |

---

## 🚀 Installation

### Prérequis
- Python 3.11+
- Clé API Anthropic ([console.anthropic.com](https://console.anthropic.com))
- Node.js 18+ (pour l'app mobile)

### 1. Cloner le projet
```bash
git clone https://github.com/ton-username/AutoChatbot.git
cd AutoChatbot
```

### 2. Installer les dépendances Python
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement
```bash
cp .env.example .env
# Ouvrir .env et renseigner ta clé API Anthropic
```

Contenu minimal du `.env` :
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
CLAUDE_MODEL=claude-haiku-4-5-20251001
PORT=8000
HOST=0.0.0.0
```

### 4. Initialiser la base de données
```bash
python seed_data.py
```

### 5. Lancer le serveur
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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
│   ├── main.py           # API FastAPI — routes et endpoints
│   ├── agent.py          # Logique IA — Abdou, outils, process_message
│   ├── models.py         # Modèles SQLAlchemy
│   ├── schemas.py        # Schémas Pydantic
│   ├── crud.py           # Opérations base de données
│   ├── database.py       # Configuration SQLite
│   ├── seed_data.py      # Données initiales (garages, pièces, fournisseurs)
│   ├── index.html        # Interface web du chatbot
│   ├── requirements.txt  # Dépendances Python
│   └── .env.example      # Template variables d'environnement
├── AutoChatbot/          # App mobile React Native (Expo)
│   ├── App.js
│   └── package.json
├── .gitignore
└── README.md
```

---

## 🤖 Outils d'Abdou

| Outil | Description |
|-------|-------------|
| `diagnostic` | Analyse les symptômes de panne |
| `identification_pieces` | Identifie une pièce par nom/modèle |
| `prix_stock` | Prix et disponibilité d'une pièce |
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
"salam"                              → Abdou répond en darija
"garage a ain beida"                 → Liste les garages avec téléphones
"ma Dacia Logan fait un bruit en freinant" → Diagnostic + conseils
"prix plaquettes de frein Symbol"    → Prix en DZD + stock
"prochaine vidange à 87000 km"       → Calcul automatique
"je veux acheter une voiture d'occasion" → Checklist complète
```

---

## 📄 Licence

Projet académique — Wilaya de Oum El Bouaghi, Algérie.  
© 2025 Benaboud Roqia & Abdrhmane Aref

---

*"Abdou est là pour toi, que tu sois à Aïn Mlila, Oum El Bouaghi, Aïn Beïda ou Aïn Fakroun."* 🔧
