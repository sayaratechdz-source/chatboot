import os
import re
import json
from typing import Dict, List, Tuple
from groq import Groq
from dotenv import load_dotenv
from database import SessionLocal
import models

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Lazy client
_client: Groq | None = None

def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY manquant!")
        _client = Groq(api_key=api_key)
    return _client

# ---------------------------------------------------------------------------
# Conversation history (in-memory, par session)
# ---------------------------------------------------------------------------
_sessions: Dict[str, List[dict]] = {}

def get_history(session_id: str) -> List[dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]

def add_to_history(session_id: str, role: str, content: str):
    history = get_history(session_id)
    history.append({"role": role, "content": content})
    # Garder max 10 échanges (20 messages) pour pas dépasser le context
    if len(history) > 20:
        _sessions[session_id] = history[-20:]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
system_prompt = (
    "انت عبدو (ابا)، ميكانيسيان خبير وصاحب في ولاية أم البواقي، الجزائر. "
    "منطقتك تغطي كامل الولاية: عين مليلة، أم البواقي، عين البيضاء، عين فكرون، وكل البلديات. "
    "تعرف جميع الغاراجات والميكانيسيان في الولاية. الأسعار بالدينار الجزائري (DZD).\n\n"
    "LANGUE: Si le message contient [LANG:AR] réponds en darija algérienne. "
    "Si [LANG:FR] réponds en français. Sinon détecte automatiquement la langue du message et réponds dans la même langue.\n\n"
    "STYLE OBLIGATOIRE:\n"
    "- Parle comme un vrai ami mécanicien algérien, chaleureux et direct.\n"
    "- INTERDIT ABSOLU: tableaux, markdown, ##titres, **gras**, JSON brut dans la réponse.\n"
    "- Texte naturel uniquement, phrases courtes, emojis avec modération.\n"
    "- JAMAIS afficher du JSON ou des accolades {} dans ta réponse finale.\n\n"
    "INTELLIGENCE ÉMOTIONNELLE:\n"
    "- Salutations: réponds chaleureusement, demande comment aider.\n"
    "- Remerciements: réponds avec plaisir.\n"
    "- Frustration: sois patient, propose aide concrète.\n"
    "- Urgence (fumée, panne route): infos essentielles en premier.\n"
    "- Questions vagues: pose UNE question pour comprendre mieux.\n"
    "- Tu te souviens du contexte de la conversation: si l'utilisateur a mentionné un symptôme avant, tu t'en souviens.\n\n"
    "RÈGLES OUTILS:\n"
    "- garage/mécanicien/atelier → trouver_garage\n"
    "- fournisseur/où acheter → trouver_fournisseur\n"
    "- panne/symptôme/bruit/fumée/tirage → diagnostic\n"
    "- prix/combien/dispo → prix_stock\n"
    "- entretien/vidange/km → entretien_vehicule\n"
    "- main d'oeuvre/coût → main_oeuvre\n"
    "- occasion/acheter voiture → checklist_occasion\n"
    "- prochaine vidange/rappel → rappel_entretien\n"
    "- danger/urgent/surchauffe → urgence_panne\n\n"
    "RÈGLES ABSOLUES:\n"
    "- Ain Beida, Ain Fakroun, Ain Mlila, Oum El Bouaghi = toutes dans ta zone.\n"
    "- Ne dis JAMAIS qu'une ville est loin ou hors zone.\n"
    "- Présente les garages: nom, ville, téléphone. Naturellement, pas en tableau.\n"
    "- Si l'utilisateur répète une info (symptôme, ville, modèle), utilise-la directement sans redemander."
)

vision_prompt = (
    "انت عبدو (ابا)، ميكانيسيان في عين مليلة، الجزائر. شوف هاذي الصورة وجاوب كيما صاحبك الميكانيسيان.\n"
    "STYLE: نص طبيعي فقط، صفر جداول، صفر markdown، صفر نجوم. جمل مباشرة وبسيطة.\n"
    "قول واش تشوف، واش فيه مشكلة، واش لازم تدير، والسعر التقريبي بالدينار إذا كان ممكن.\n"
    "جاوب بنفس لغة رسالة المستخدم (فرنسية، عربية، دارجة)."
)

# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------
_SOCIAL_KW = [
    "salam", "bonjour", "bonsoir", "salut", "ahlan", "wach rak", "labas", "la bas",
    "merci", "chokran", "barak allah", "shukran", "thank",
    "bslama", "a bientot", "au revoir", "yallah bye", "bye", "ciao",
    "comment tu vas", "ca va", "kif rak", "kif nta",
    "bravo", "t es fort", "bien joue", "chapeau",
    "qui es tu", "tu es qui", "c est quoi", "tu fais quoi",
]

_TECH_KW = [
    "garage", "piece", "panne", "frein", "moteur", "voiture", "prix",
    "mecanicien", "vidange", "huile", "tirage", "bruit", "fumee", "fume",
    "tourne", "demarre", "vitesse", "embrayage", "batterie", "direction",
    "pneu", "suspension", "distribution", "courroie", "filtre", "bougie",
    "hdi", "tdi", "essence", "diesel", "kilometrage", "surchauffe",
    "دخان", "يدخن", "محرك", "فرامل", "بطارية", "علبة", "كلاج", "ميكانيك",
    "تيراج", "حرارة", "يشتغل", "يبدا", "ديزل",
]

_VILLES_MAP = {
    "ain beida": "Aïn Beida", "beida": "Aïn Beida", "عين البيضاء": "Aïn Beida",
    "ain fakroun": "Aïn Fakroun", "fakroun": "Aïn Fakroun", "عين فكرون": "Aïn Fakroun",
    "ain mlila": "Aïn Mlila", "mlila": "Aïn Mlila", "عين مليلة": "Aïn Mlila",
    "oum el bouaghi": "Oum El Bouaghi", "oum bouaghi": "Oum El Bouaghi",
    "oeb": "Oum El Bouaghi", "bouaghi": "Oum El Bouaghi", "أم البواقي": "Oum El Bouaghi",
}

_GARAGE_KW = [
    "garage", "mecanicien", "atelier", "depanneur", "mecano",
    "reparer", "reparation", "mecanique", "ميكانيك", "ورشة", "كراج",
]

# ---------------------------------------------------------------------------
# Tools definition
# ---------------------------------------------------------------------------
tools = [
    {"type": "function", "function": {"name": "diagnostic",
        "description": "Analyse les symptômes d'une panne automobile et donne un diagnostic.",
        "parameters": {"type": "object", "properties": {"symptomes": {"type": "string"}}, "required": ["symptomes"]}}},
    {"type": "function", "function": {"name": "identification_pieces",
        "description": "Identifie une pièce pour le véhicule.",
        "parameters": {"type": "object", "properties": {
            "nom_piece": {"type": "string"}, "modele_vehicule": {"type": "string"}},
            "required": ["nom_piece"]}}},
    {"type": "function", "function": {"name": "prix_stock",
        "description": "Vérifie le prix et le stock d'une pièce.",
        "parameters": {"type": "object", "properties": {"reference_piece": {"type": "string"}}, "required": ["reference_piece"]}}},
    {"type": "function", "function": {"name": "trouver_garage",
        "description": "Trouve un garage ou mécanicien dans la wilaya de Oum El Bouaghi.",
        "parameters": {"type": "object", "properties": {
            "type_reparation": {"type": "string"}, "ville": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "trouver_fournisseur",
        "description": "Trouve un fournisseur de pièces automobiles.",
        "parameters": {"type": "object", "properties": {
            "specialite": {"type": "string"}, "ville": {"type": "string"}}, "required": ["specialite"]}}},
    {"type": "function", "function": {"name": "entretien_vehicule",
        "description": "Programme d'entretien pour un véhicule selon le kilométrage.",
        "parameters": {"type": "object", "properties": {
            "modele": {"type": "string"}, "kilometrage": {"type": "integer"}}, "required": ["modele"]}}},
    {"type": "function", "function": {"name": "main_oeuvre",
        "description": "Estime le coût de main d'oeuvre pour une réparation.",
        "parameters": {"type": "object", "properties": {"type_reparation": {"type": "string"}}, "required": ["type_reparation"]}}},
    {"type": "function", "function": {"name": "checklist_occasion",
        "description": "Checklist pour inspecter une voiture d'occasion avant achat.",
        "parameters": {"type": "object", "properties": {"modele": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "rappel_entretien",
        "description": "Calcule la prochaine échéance d'entretien ou de vidange.",
        "parameters": {"type": "object", "properties": {
            "derniere_vidange_km": {"type": "integer"}, "km_actuel": {"type": "integer"}}, "required": ["km_actuel"]}}},
    {"type": "function", "function": {"name": "urgence_panne",
        "description": "Conseils urgents en cas de panne grave ou dangereuse.",
        "parameters": {"type": "object", "properties": {"symptome_urgent": {"type": "string"}}, "required": ["symptome_urgent"]}}},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _clean(text: str) -> str:
    """Nettoie le markdown et le JSON accidentel dans la réponse."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    text = re.sub(r"#{1,6} ?", "", text)
    text = re.sub(r"`+[^`]*`+", "", text)
    # Supprime les blocs JSON accidentels { ... }
    text = re.sub(r"\{[^}]{0,200}\}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------
def execute_tool(name: str, inputs: dict) -> str:
    db = SessionLocal()
    try:
        if name == "diagnostic":
            s = inputs.get("symptomes", "").lower()
            if any(k in s for k in ["frein", "grinc", "pedale", "stop", "فرامل"]):
                return "Usure probable des plaquettes de frein. Vérifier épaisseur et disques. Intervention urgente si < 3mm."
            elif any(k in s for k in ["fumee", "fume", "دخان", "يدخن", "smoke"]):
                return "Fumée moteur: peut être joint de culasse, turbo, huile sur collecteur. Vérifier niveau huile et couleur fumée (blanche=liquide, noire=riche, bleue=huile)."
            elif any(k in s for k in ["tirage", "تيراج", "puissance", "accelerat", "lent"]):
                return "Manque de puissance/tirage sur 1.6 HDi: vérifier filtre à air encrassé, filtre gasoil, turbo (jeu axial), vanne EGR encrassée, injecteurs. Diagnostic OBD recommandé."
            elif any(k in s for k in ["moteur", "vibr", "cliquetis", "bruit", "محرك"]):
                return "Bruit/vibration moteur: vérifier bougies, support moteur, distribution. Possible problème d'allumage ou de suspension moteur."
            elif any(k in s for k in ["batterie", "demarr", "electr", "بطارية"]):
                return "Batterie faible ou alternateur défaillant. Tester tension: 12.6V à vide, 13.8-14.4V moteur tournant."
            elif any(k in s for k in ["surchauffe", "temperature", "chauffe", "حرارة"]):
                return "Surchauffe: vérifier niveau liquide refroidissement, thermostat, pompe à eau, radiateur bouché. Ne jamais ouvrir le radiateur chaud!"
            elif any(k in s for k in ["direction", "volant", "dur"]):
                return "Direction dure: vérifier niveau huile direction assistée, courroie pompe direction, crémaillère."
            elif any(k in s for k in ["embrayage", "patine", "vitesse", "كلاج"]):
                return "Embrayage usé: symptômes = patinage, pédale molle ou dure, bruit au démarrage. Kit embrayage à prévoir."
            return "Plusieurs causes possibles. Décris mieux le symptôme: quand ça arrive, bruit, fumée, voyant allumé?"

        elif name == "identification_pieces":
            nom = inputs.get("nom_piece", "").lower()
            pieces = db.query(models.Piece).filter(models.Piece.nom.ilike(f"%{nom}%")).limit(3).all()
            if pieces:
                return "Pièces trouvées: " + " | ".join(f"{p.nom} (Ref: {p.reference}) - {p.prix:.0f} DZD - Stock: {p.stock}" for p in pieces)
            return f"Aucune pièce trouvée pour '{nom}' dans la base."

        elif name == "prix_stock":
            ref = inputs.get("reference_piece", "").lower()
            p = db.query(models.Piece).filter(
                (models.Piece.reference.ilike(f"%{ref}%")) | (models.Piece.nom.ilike(f"%{ref}%"))
            ).first()
            if p:
                dispo = "Disponible" if p.stock > 0 else "Rupture de stock"
                return f"{p.nom} | Ref: {p.reference} | Prix: {p.prix:.0f} DZD | Stock: {p.stock} | {dispo}. {p.description}"
            return f"Pièce '{ref}' non trouvée dans la base."

        elif name == "trouver_fournisseur":
            specialite = inputs.get("specialite", "")
            ville = inputs.get("ville", "")
            query = db.query(models.Fournisseur)
            if specialite:
                query = query.filter(models.Fournisseur.specialite.ilike(f"%{specialite}%"))
            if ville:
                query = query.filter(models.Fournisseur.ville.ilike(f"%{ville}%"))
            fournisseurs = query.limit(4).all()
            if not fournisseurs:
                fournisseurs = db.query(models.Fournisseur).limit(4).all()
            return "Fournisseurs: " + " | ".join(f"{f.nom} ({f.ville}) Tel: {f.telephone}" for f in fournisseurs)

        elif name == "trouver_garage":
            type_rep = inputs.get("type_reparation", "")
            ville = inputs.get("ville", "")
            query = db.query(models.Garage)
            if ville:
                query = query.filter(models.Garage.ville == ville)
            if type_rep:
                garages = query.filter(models.Garage.specialite.ilike(f"%{type_rep}%")).limit(4).all()
                if not garages:
                    garages = query.limit(4).all()
            else:
                garages = query.limit(4).all()
            if not garages:
                garages = db.query(models.Garage).limit(4).all()
            return "Garages: " + " | ".join(f"{g.nom} ({g.ville}) Tel: {g.telephone}" for g in garages)

        elif name == "entretien_vehicule":
            modele = inputs.get("modele", "votre véhicule")
            km = inputs.get("kilometrage", 0)
            tasks = []
            if km == 0 or km % 10000 < 1500:
                tasks.append("vidange huile + filtre huile")
            if km == 0 or km % 15000 < 1500:
                tasks.append("filtre à air")
            if km == 0 or km % 30000 < 1500:
                tasks.append("bougies, filtre carburant")
            if km == 0 or km % 60000 < 1500:
                tasks.append("courroie de distribution")
            if not tasks:
                tasks = ["vérification générale", "niveaux"]
            return f"Entretien {modele} à {km} km: {', '.join(tasks)}. Coût estimé: 3500-8000 DZD selon pièces."

        elif name == "main_oeuvre":
            t = inputs.get("type_reparation", "").lower()
            tarifs = {
                "vidange": "800-1200 DZD", "frein": "1500-2500 DZD", "embrayage": "4000-7000 DZD",
                "distribution": "5000-9000 DZD", "climatisation": "2000-4000 DZD",
                "electricite": "1500-3000 DZD", "carrosserie": "3000-10000 DZD",
                "pneu": "300-500 DZD/pneu", "geometrie": "1500-2500 DZD",
                "suspension": "2000-4000 DZD", "injection": "3000-6000 DZD",
                "turbo": "3000-6000 DZD",
            }
            for key, val in tarifs.items():
                if key in t:
                    return f"Main d'oeuvre {t}: environ {val}. Prix final selon garage."
            return f"Main d'oeuvre {t}: entre 1000 et 5000 DZD selon complexité."

        elif name == "checklist_occasion":
            modele = inputs.get("modele", "la voiture")
            return (f"Checklist {modele} d'occasion: 1.Carrosserie rouille/impacts. "
                    "2.Moteur fuites/fumée/bruit. 3.Boîte vitesses passages fluides. "
                    "4.Freins épaisseur plaquettes. 5.Pneus usure/âge. "
                    "6.Clim/électrique. 7.Documents carte grise+CT. 8.Essai 15min minimum. "
                    "Conseil: fais vérifier par un mécanicien avant achat.")

        elif name == "rappel_entretien":
            km_actuel = inputs.get("km_actuel", 0)
            derniere = inputs.get("derniere_vidange_km", 0)
            if derniere:
                parcourus = km_actuel - derniere
                restant = 10000 - parcourus
                if restant <= 0:
                    return f"Vidange en retard de {abs(restant)} km! À faire immédiatement."
                return f"Prochaine vidange dans {restant} km (à {derniere + 10000} km). Parcouru: {parcourus} km."
            prochain = ((km_actuel // 10000) + 1) * 10000
            return f"Prochaine vidange recommandée à {prochain} km (dans {prochain - km_actuel} km)."

        elif name == "urgence_panne":
            s = inputs.get("symptome_urgent", "").lower()
            if any(k in s for k in ["feu", "incendie", "brule", "حريق"]):
                return "DANGER! Arrêtez, coupez moteur, sortez, éloignez-vous. Appelez le 14."
            elif any(k in s for k in ["surchauffe", "temperature", "rouge", "chauffe"]):
                return "Arrêtez le moteur! Ne pas ouvrir le radiateur à chaud. Attendez 30min. Vérifiez niveau froid."
            elif any(k in s for k in ["frein", "pedale", "plus de frein"]):
                return "Rétrógradez, frein à main doucement, cherchez obstacle mou. Ne paniquez pas."
            return "Arrêtez-vous, feux de détresse. Appelez un dépanneur de la wilaya."

    finally:
        db.close()
    return "Information non disponible."

# ---------------------------------------------------------------------------
# Image analysis
# ---------------------------------------------------------------------------
async def analyze_image(image_b64: str, media_type: str, user_message: str) -> str:
    try:
        response = get_client().chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {"role": "system", "content": vision_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_message if user_message.strip() else "Décris cette image"},
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_b64}"}}
                ]}
            ],
            max_tokens=1024
        )
        return _clean(response.choices[0].message.content)
    except Exception as e:
        print(f"Erreur vision: {e}")
        return "ما قدرتش نحلل هاذي الصورة، عاود حاول."

# ---------------------------------------------------------------------------
# Main message processing - avec historique de conversation
# ---------------------------------------------------------------------------
async def process_message(user_message: str, session_id: str, image_b64=None, media_type=None):
    tools_triggered = []

    if image_b64:
        reply = await analyze_image(image_b64, media_type or "image/jpeg", user_message)
        add_to_history(session_id, "user", user_message or "image")
        add_to_history(session_id, "assistant", reply)
        return reply, ["vision_analysis"]

    msg_lower = user_message.lower().strip()

    # Détecter si c'est purement social (sans contenu technique)
    has_tech = any(k in msg_lower for k in _TECH_KW)
    is_social_only = any(kw in msg_lower for kw in _SOCIAL_KW) and not has_tech
    is_short_nontechnical = len(msg_lower.split()) <= 3 and not has_tech

    # Détecter ville
    detected_ville = ""
    for key, val in _VILLES_MAP.items():
        if key in msg_lower:
            detected_ville = val
            break

    # Construire les messages avec historique
    history = get_history(session_id)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Force garage tool si demande directe
    force_garage = any(kw in msg_lower for kw in _GARAGE_KW)
    if detected_ville and not force_garage:
        if any(k in msg_lower for k in ["mecani", "reparer", "depann", "trouver", "ورشة"]):
            force_garage = True

    if force_garage:
        tool_inputs = {"type_reparation": "", "ville": detected_ville}
        for kw in ["frein", "embrayage", "vidange", "distribution", "electricite",
                   "climatisation", "injection", "turbo", "suspension", "pneu", "batterie"]:
            if kw in msg_lower:
                tool_inputs["type_reparation"] = kw
                break
        tool_result = execute_tool("trouver_garage", tool_inputs)
        tools_triggered.append("trouver_garage")

        messages[-1]["content"] = (
            f"{user_message}\n\n[INFO SYSTÈME - NE PAS AFFICHER EN JSON]: "
            f"Garages trouvés dans la base de données: {tool_result}\n"
            "Présente ces garages naturellement: nom, ville, téléphone. Pas de JSON, pas de tableau."
        )

        try:
            response = get_client().chat.completions.create(
                model=GROQ_MODEL, messages=messages, max_tokens=1024
            )
            reply = _clean(response.choices[0].message.content) or _clean(tool_result)
            add_to_history(session_id, "user", user_message)
            add_to_history(session_id, "assistant", reply)
            return reply, tools_triggered
        except Exception as e:
            print("Erreur forced garage:", e)
            return _clean(tool_result), tools_triggered

    # Flow social simple (sans outils)
    if is_social_only or is_short_nontechnical:
        try:
            response = get_client().chat.completions.create(
                model=GROQ_MODEL, messages=messages, max_tokens=512
            )
            reply = _clean(response.choices[0].message.content) or "أهلاً! كيف نقدر نساعدك؟"
            add_to_history(session_id, "user", user_message)
            add_to_history(session_id, "assistant", reply)
            return reply, []
        except Exception as e:
            print("Erreur social:", e)
            return "أهلاً! كيف نقدر نساعدك؟", []

    # Flow normal avec function calling
    try:
        response = get_client().chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )

        while response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            messages.append(response.choices[0].message)

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tools_triggered.append(tool_name)
                tool_result = execute_tool(tool_name, tool_args)
                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call.id
                })

            response = get_client().chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024
            )

        reply = _clean(response.choices[0].message.content) or "ما عندي رد، عاود حاول."
        add_to_history(session_id, "user", user_message)
        add_to_history(session_id, "assistant", reply)
        return reply, tools_triggered

    except Exception as e:
        print("Erreur Groq:", e)
        return "عندي مشكلة تقنية صغيرة، عاود في لحظة!", tools_triggered
