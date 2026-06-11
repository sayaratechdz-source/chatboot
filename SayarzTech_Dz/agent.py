import os
import re
import random
import time
from typing import List, Tuple
import httpx
from dotenv import load_dotenv
from database import SessionLocal
import models

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def _get_gemini_url():
    return f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Session history store
_session_store: dict = {}
SESSION_TTL_SECONDS = 3600
MAX_SESSIONS = 500


def _get_history(session_id: str) -> list:
    now = time.time()
    expired = [sid for sid, v in _session_store.items()
               if now - v["last_access"] > SESSION_TTL_SECONDS]
    for sid in expired:
        del _session_store[sid]
    if session_id not in _session_store and len(_session_store) >= MAX_SESSIONS:
        oldest = min(_session_store, key=lambda sid: _session_store[sid]["last_access"])
        del _session_store[oldest]
    if session_id not in _session_store:
        _session_store[session_id] = {"messages": [], "last_access": now}
    _session_store[session_id]["last_access"] = now
    return _session_store[session_id]["messages"]


def _append_history(session_id: str, role: str, content: str):
    history = _get_history(session_id)
    # Gemini uses "user" and "model" roles
    gemini_role = "model" if role == "assistant" else "user"
    history.append({"role": gemini_role, "parts": [{"text": content}]})
    if len(history) > 20:
        _session_store[session_id]["messages"] = history[-20:]


system_prompt = (
    "Tu es Abdou (aussi appele Abba), mecanicien expert et ami dans la wilaya de Oum El Bouaghi, Algerie. "
    "Ta zone couvre TOUTE la wilaya: Ain Mlila, Oum El Bouaghi, Ain Beida, Ain Fakroun, et toutes les communes. "
    "Tu connais TOUS les garages et mecaniciens de la wilaya. Les prix sont en Dinars Algeriens (DZD).\n\n"
    "LANGUE: Si [LANG:AR] reponds en darija algerienne naturelle. Si [LANG:FR] reponds en francais. Sinon detecte automatiquement.\n\n"
    "STYLE OBLIGATOIRE: Parle comme un vrai ami mecanicien algerien. "
    "INTERDIT ABSOLU: tableaux, markdown, titres avec ##, asterisques **gras**. "
    "Ecris en texte naturel, phrases courtes, ton chaleureux et direct. Emojis avec moderation.\n\n"
    "Reponds toujours en texte simple, sans formatting special."
)

vision_prompt = (
    "Tu es Abdou (Abba), mecanicien a Ain Mlila, Algerie. Regarde cette image et reponds comme un vrai ami mecanicien.\n"
    "STYLE OBLIGATOIRE: texte naturel et humain, ZERO tableaux, ZERO markdown, ZERO asterisques. Phrases directes et simples.\n"
    "Dis ce que tu vois, ce qui ne va pas, ce qu il faut faire, et le prix approximatif en DZD si applicable.\n"
    "Sois concret: si c est grave dis-le clairement, si c est simple rassure le client.\n"
    "Reponds dans la langue du message de l utilisateur (francais, arabe, darija)."
)

_SOCIAL_KW = [
    "salam", "bonjour", "bonsoir", "salut", "ahlan", "wach rak", "labas", "la bas",
    "merci", "chokran", "barak allah", "shukran", "thank",
    "bslama", "a bientot", "au revoir", "yallah bye", "bye", "ciao", "tchao",
    "comment tu vas", "ca va", "kif rak", "kif nta",
    "bravo", "t es fort", "bien joue", "chapeau", "excellent",
    "nul", "inutile", "ca marche pas", "pas bien",
    "qui es tu", "tu es qui", "c est quoi", "tu fais quoi",
    "aide moi", "help", "aidez moi",
]

_VILLES_MAP = {
    "ain beida": "Aïn Beida", "beida": "Aïn Beida",
    "ain fakroun": "Aïn Fakroun", "fakroun": "Aïn Fakroun",
    "ain mlila": "Aïn Mlila", "mlila": "Aïn Mlila",
    "oum el bouaghi": "Oum El Bouaghi", "oum bouaghi": "Oum El Bouaghi",
    "oeb": "Oum El Bouaghi", "bouaghi": "Oum El Bouaghi",
}

_GARAGE_KW = [
    "garage", "mecanicien", "mecanicienne", "atelier", "depanneur",
    "mecano", "reparer", "reparation", "mecanique",
]


def _clean(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    text = re.sub(r"#{1,6} ?", "", text)
    text = re.sub(r"`+", "", text)
    return text.strip()


async def _call_gemini(messages: list, system: str = "") -> str:
    """Call OpenRouter API (compatible with OpenAI format)."""
    async with httpx.AsyncClient(timeout=30) as client:
        # Convert Gemini-format messages to OpenAI format
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        for m in messages:
            role = "assistant" if m["role"] == "model" else "user"
            content = m["parts"][0]["text"] if "parts" in m else m.get("content", "")
            openai_messages.append({"role": role, "content": content})

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": openai_messages,
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        resp = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json; charset=utf-8",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "SayaraTech Chatbot"
            },
            json=payload
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_gemini_vision(image_b64: str, media_type: str, user_message: str) -> str:
    """Call OpenRouter Vision API with image."""
    async with httpx.AsyncClient(timeout=30) as client:
        content = []
        if user_message.strip():
            content.append({"type": "text", "text": user_message + "\n\n" + vision_prompt})
        else:
            content.append({"type": "text", "text": vision_prompt})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{image_b64}"}
        })

        payload = {
            "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 1024,
        }

        resp = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json; charset=utf-8",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "SayaraTech Chatbot"
            },
            json=payload
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def execute_tool(name: str, inputs: dict) -> str:
    db = SessionLocal()
    try:
        if name == "diagnostic":
            s = inputs.get("symptomes", "").lower()
            if any(k in s for k in ["frein", "grinc", "pedale", "stop"]):
                return "Usure probable des plaquettes de frein. Intervention urgente sous 500 km."
            elif any(k in s for k in ["moteur", "vibr", "cliquetis", "bruit"]):
                return "Possible probleme bougies, support moteur ou distribution."
            elif any(k in s for k in ["batterie", "demarr", "electr"]):
                return "Batterie faible ou alternateur defaillant. Tester tension: 13.8-14.4V moteur tournant."
            elif any(k in s for k in ["surchauffe", "temperature", "fumee"]):
                return "Probleme refroidissement. Verifier niveau liquide, thermostat, pompe a eau."
            elif any(k in s for k in ["direction", "volant", "dur"]):
                return "Probleme direction assistee. Verifier niveau huile direction."
            elif any(k in s for k in ["embrayage", "patine", "vitesse"]):
                return "Embrayage use. Verifier jeu pedale et disque."
            return "Plusieurs causes possibles. Inspection visuelle recommandee."

        elif name == "trouver_garage":
            type_rep = inputs.get("type_reparation", "")
            ville = inputs.get("ville", "")
            query = db.query(models.Garage)
            if ville:
                query = query.filter(models.Garage.ville == ville)
            if type_rep:
                q2 = query.filter(models.Garage.specialite.ilike(f"%{type_rep}%"))
                garages = q2.limit(5).all()
                if not garages:
                    garages = query.limit(5).all()
            else:
                garages = query.limit(5).all()
            if not garages:
                garages = db.query(models.Garage).limit(5).all()
            return "Garages:\n" + "".join(
                f"- {g.nom} | {g.ville} | Tel: {g.telephone} | {g.adresse}\n" for g in garages
            )

        elif name == "prix_stock":
            ref = inputs.get("reference_piece", "").lower()
            p = db.query(models.Piece).filter(
                (models.Piece.reference.ilike(f"%{ref}%")) | (models.Piece.nom.ilike(f"%{ref}%"))
            ).first()
            if p:
                dispo = "Disponible" if p.stock > 0 else "Rupture de stock"
                return f"{p.nom} | Ref: {p.reference} | Prix: {p.prix:.0f} DZD | Stock: {p.stock} | {dispo}"
            return f"Piece '{ref}' non trouvee."

        elif name == "entretien_vehicule":
            modele = inputs.get("modele", "votre vehicule")
            km = inputs.get("kilometrage", 0)
            tasks = []
            if km == 0 or km % 5000 < 1000:
                tasks.append("vidange huile moteur + filtre huile")
            if km == 0 or km % 10000 < 1000:
                tasks.append("filtre a air, filtre habitacle")
            if km == 0 or km % 20000 < 1000:
                tasks.append("bougies d allumage, filtre carburant")
            if not tasks:
                tasks = ["vidange huile moteur", "verification generale"]
            return f"Entretien pour {modele} a {km} km: " + ", ".join(tasks) + ". Cout estimatif: 3500-8000 DZD."

        elif name == "urgence_panne":
            s = inputs.get("symptome_urgent", "").lower()
            if any(k in s for k in ["fumee", "feu", "incendie", "brule"]):
                return "DANGER! Arretez immediatement, coupez le moteur, sortez du vehicule. Appelez le 14 (pompiers)."
            elif any(k in s for k in ["surchauffe", "temperature", "rouge"]):
                return "Arretez le moteur immediatement! Ne pas ouvrir le radiateur a chaud. Attendez 30 min."
            elif any(k in s for k in ["frein", "pedale", "plus de frein"]):
                return "Freins defaillants: retrogradez progressivement, utilisez le frein a main doucement."
            return "Arretez-vous en securite, mettez les feux de detresse. Appelez un depanneur."

    finally:
        db.close()
    return "Information non disponible."


async def process_message(user_message: str, session_id: str, image_b64=None, media_type=None):
    tools_triggered = []

    # Vision
    if image_b64:
        try:
            reply = await _call_gemini_vision(image_b64, media_type or "image/jpeg", user_message)
            reply = _clean(reply)
        except Exception as e:
            print(f"Erreur vision Gemini: {e}")
            reply = "Desole, je n ai pas pu analyser cette image."
        _append_history(session_id, "user", user_message or "[image]")
        _append_history(session_id, "assistant", reply)
        return reply, ["vision_analysis"]

    msg_lower = user_message.lower().strip()
    history = _get_history(session_id)

    # Detect garage keywords
    detected_ville = ""
    for key, val in _VILLES_MAP.items():
        if key in msg_lower:
            detected_ville = val
            break

    force_garage = any(kw in msg_lower for kw in _GARAGE_KW)

    # If garage keyword, fetch from DB first then send to Gemini
    extra_context = ""
    if force_garage:
        tool_inputs = {"type_reparation": "", "ville": detected_ville}
        for kw in ["frein", "embrayage", "vidange", "distribution", "electricite",
                   "carrosserie", "climatisation", "injection", "suspension", "pneu"]:
            if kw in msg_lower:
                tool_inputs["type_reparation"] = kw
                break
        extra_context = execute_tool("trouver_garage", tool_inputs)
        tools_triggered.append("trouver_garage")

    # Detect urgency
    if any(k in msg_lower for k in ["fumee", "surchauffe", "plus de frein", "danger", "urgent"]):
        extra_context += "\n" + execute_tool("urgence_panne", {"symptome_urgent": user_message})
        tools_triggered.append("urgence_panne")

    # Build messages for Gemini
    messages = list(history[-10:])
    user_content = user_message
    if extra_context:
        user_content = f"{user_message}\n\n[Donnees systeme: {extra_context}]"
    messages.append({"role": "user", "parts": [{"text": user_content}]})

    try:
        raw = await _call_gemini(messages, system_prompt)
        reply = _clean(raw)
        _append_history(session_id, "user", user_message)
        _append_history(session_id, "assistant", reply)
        return reply, tools_triggered
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        if extra_context:
            return _clean(extra_context), tools_triggered
        return "Desole, j ai un petit souci technique. Reessaie dans un instant!", tools_triggered
