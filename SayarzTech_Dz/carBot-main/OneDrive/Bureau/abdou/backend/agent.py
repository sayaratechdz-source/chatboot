import os
import re
import random
from typing import List, Tuple
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from database import SessionLocal
import models

load_dotenv()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

tools = [
    {"name": "diagnostic", "description": "Analyse les symptomes d'une panne automobile.", "input_schema": {"type": "object", "properties": {"symptomes": {"type": "string"}}, "required": ["symptomes"]}},
    {"name": "identification_pieces", "description": "Identifie une piece pour le vehicule.", "input_schema": {"type": "object", "properties": {"nom_piece": {"type": "string"}, "modele_vehicule": {"type": "string"}}, "required": ["nom_piece"]}},
    {"name": "prix_stock", "description": "Verifie le prix et le stock d'une piece.", "input_schema": {"type": "object", "properties": {"reference_piece": {"type": "string"}}, "required": ["reference_piece"]}},
    {"name": "commandes", "description": "Prepare une commande pour des pieces.", "input_schema": {"type": "object", "properties": {"pieces": {"type": "array", "items": {"type": "string"}}}, "required": ["pieces"]}},
    {"name": "trouver_fournisseur", "description": "Trouve un fournisseur de pieces.", "input_schema": {"type": "object", "properties": {"specialite": {"type": "string"}, "ville": {"type": "string"}}, "required": ["specialite"]}},
    {"name": "trouver_garage", "description": "Trouve un garage ou mecanicien dans la wilaya.", "input_schema": {"type": "object", "properties": {"type_reparation": {"type": "string"}, "ville": {"type": "string"}}, "required": []}},
    {"name": "entretien_vehicule", "description": "Programme d'entretien pour un vehicule.", "input_schema": {"type": "object", "properties": {"modele": {"type": "string"}, "kilometrage": {"type": "integer"}}, "required": ["modele"]}},
    {"name": "main_oeuvre", "description": "Estime le cout de main d oeuvre.", "input_schema": {"type": "object", "properties": {"type_reparation": {"type": "string"}}, "required": ["type_reparation"]}},
    {"name": "checklist_occasion", "description": "Checklist pour inspecter une voiture d occasion.", "input_schema": {"type": "object", "properties": {"modele": {"type": "string"}}, "required": []}},
    {"name": "rappel_entretien", "description": "Calcule la prochaine echeance d entretien.", "input_schema": {"type": "object", "properties": {"derniere_vidange_km": {"type": "integer"}, "km_actuel": {"type": "integer"}}, "required": ["km_actuel"]}},
    {"name": "urgence_panne", "description": "Conseils urgents en cas de panne grave.", "input_schema": {"type": "object", "properties": {"symptome_urgent": {"type": "string"}}, "required": ["symptome_urgent"]}},
]

system_prompt = (
    "Tu es Abdou (aussi appele Abba), mecanicien expert et ami dans la wilaya de Oum El Bouaghi, Algerie. "
    "Ta zone couvre TOUTE la wilaya: Ain Mlila, Oum El Bouaghi, Ain Beida, Ain Fakroun, et toutes les communes. "
    "Tu connais TOUS les garages et mecaniciens de la wilaya. Les prix sont en Dinars Algeriens (DZD).\n\n"
    "LANGUE: Si [LANG:AR] reponds en darija algerienne naturelle. Si [LANG:FR] reponds en francais. Sinon detecte automatiquement.\n\n"
    "INTELLIGENCE EMOTIONNELLE ET HUMAINE:\n"
    "- Salutations (salam, bonjour, ahlan, wach rak, labas): reponds chaleureusement, demande comment tu peux aider.\n"
    "- Remerciements (merci, chokran, barak allah fik): reponds avec plaisir, reste disponible.\n"
    "- Frustration/colere (ca marche pas, nul, inutile): sois patient, propose de l aide concrete.\n"
    "- Urgence (vite, urgent, en panne sur la route): reagis rapidement, donne les infos essentielles en premier.\n"
    "- Questions vagues (j ai un probleme, ma voiture fait un bruit): pose une question simple pour comprendre mieux.\n"
    "- Bonne humeur/blague: reponds avec legerte et humour algerien naturel.\n"
    "- Compliments (t es fort, bravo): accepte avec modestie et humour.\n"
    "- Au revoir (bslama, a bientot, yallah bye): reponds chaleureusement, souhaite bonne route.\n\n"
    "STYLE OBLIGATOIRE: Parle comme un vrai ami mecanicien algerien. "
    "INTERDIT ABSOLU: tableaux, markdown, titres avec ##, asterisques **gras**. "
    "Ecris en texte naturel, phrases courtes, ton chaleureux et direct. Emojis avec moderation.\n\n"
    "REGLES OUTILS:\n"
    "- garage/mecanicien/atelier/depanneur -> trouver_garage immediatement\n"
    "- ou acheter/fournisseur -> trouver_fournisseur\n"
    "- panne/symptome/bruit -> diagnostic\n"
    "- prix/combien/dispo -> prix_stock\n"
    "- commander -> commandes\n"
    "- entretien/vidange/kilometrage -> entretien_vehicule\n"
    "- main d oeuvre/cout pose -> main_oeuvre\n"
    "- occasion/acheter voiture -> checklist_occasion\n"
    "- prochaine vidange/rappel -> rappel_entretien\n"
    "- danger/urgent/fumer/surchauffe -> urgence_panne\n\n"
    "REGLES ABSOLUES:\n"
    "- Ain Beida, Ain Fakroun, Ain Mlila, Oum El Bouaghi = TOUTES dans ta zone, tu les connais toutes.\n"
    "- Ne dis JAMAIS qu une ville est hors zone ou loin.\n"
    "- Quand tu recois des garages, presente-les directement: nom, ville, telephone. C est tout.\n"
    "- Ne commente pas la distance entre les villes."
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
    "mecano", "rv motor", "revix", "wr auto", "service rapide", "911",
    "rassim", "nabile", "lamine", "salah", "bilal", "hamza", "farid",
    "walid", "hassen", "riad", "nassim", "djamel", "samir", "zine", "mehdi",
    "reparer", "reparation", "mecanique",
]

def _clean(text: str) -> str:
    text = re.sub(r"[*][*]([^*]+)[*][*]", r"\\1", text)
    text = re.sub(r"[*]([^*\n]+)[*]", r"\\1", text)
    text = re.sub(r"#{1,6} ?", "", text)
    text = re.sub(r"`+", "", text)
    return text.strip()

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

        elif name == "identification_pieces":
            nom = inputs.get("nom_piece", "").lower()
            pieces = db.query(models.Piece).filter(models.Piece.nom.ilike(f"%{nom}%")).limit(3).all()
            if pieces:
                return "Pieces trouvees:\n" + "".join(f"- {p.nom} (Ref: {p.reference}) - {p.prix:.0f} DZD - Stock: {p.stock}\n" for p in pieces)
            return f"Aucune piece trouvee pour '{nom}'."

        elif name == "prix_stock":
            ref = inputs.get("reference_piece", "").lower()
            p = db.query(models.Piece).filter(
                (models.Piece.reference.ilike(f"%{ref}%")) | (models.Piece.nom.ilike(f"%{ref}%"))
            ).first()
            if p:
                dispo = "Disponible" if p.stock > 0 else "Rupture de stock"
                return f"{p.nom} | Ref: {p.reference} | Prix: {p.prix:.0f} DZD | Stock: {p.stock} | {dispo}\n{p.description}"
            return f"Piece '{ref}' non trouvee."

        elif name == "commandes":
            pieces_list = inputs.get("pieces", [])
            total, details = 0, []
            for nom_piece in pieces_list:
                p = db.query(models.Piece).filter(models.Piece.nom.ilike(f"%{nom_piece}%")).first()
                if p and p.stock > 0:
                    total += p.prix
                    details.append(f"{p.nom}: {p.prix:.0f} DZD")
            if details:
                import random as _r
                return f"Commande OK - {', '.join(details)} - Total: {total:.0f} DZD - N: CMD-{_r.randint(1000,9999)}"
            return "Aucune piece disponible."

        elif name == "trouver_fournisseur":
            specialite = inputs.get("specialite", "")
            ville = inputs.get("ville", "")
            query = db.query(models.Fournisseur)
            if specialite:
                query = query.filter(models.Fournisseur.specialite.ilike(f"%{specialite}%"))
            if ville:
                query = query.filter(models.Fournisseur.ville.ilike(f"%{ville}%"))
            fournisseurs = query.limit(5).all()
            if not fournisseurs:
                fournisseurs = db.query(models.Fournisseur).limit(5).all()
            return "Fournisseurs:\n" + "".join(f"- {f.nom} | {f.ville} | Tel: {f.telephone} | {f.adresse}\n" for f in fournisseurs)

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
            return "Garages:\n" + "".join(f"- {g.nom} | {g.ville} | Tel: {g.telephone} | {g.adresse}\n" for g in garages)

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
            if km == 0 or km % 40000 < 1000:
                tasks.append("courroie de distribution (si applicable)")
            if not tasks:
                tasks = ["vidange huile moteur", "verification generale"]
            return f"Entretien pour {modele} a {km} km: " + ", ".join(tasks) + ". Cout estimatif: 3500-8000 DZD selon les pieces."

        elif name == "main_oeuvre":
            t = inputs.get("type_reparation", "").lower()
            tarifs = {
                "vidange": "800-1200 DZD", "frein": "1500-2500 DZD", "embrayage": "4000-7000 DZD",
                "distribution": "5000-9000 DZD", "climatisation": "2000-4000 DZD",
                "electricite": "1500-3000 DZD", "carrosserie": "3000-10000 DZD",
                "pneu": "300-500 DZD/pneu", "geometrie": "1500-2500 DZD",
                "suspension": "2000-4000 DZD", "injection": "3000-6000 DZD",
            }
            for key, val in tarifs.items():
                if key in t:
                    return f"Main d oeuvre pour {t}: environ {val}. Prix final selon le garage."
            return f"Main d oeuvre pour {t}: entre 1000 et 5000 DZD selon la complexite. Demandez un devis au garage."

        elif name == "checklist_occasion":
            modele = inputs.get("modele", "la voiture")
            return (
                f"Checklist pour inspecter {modele} d occasion: "
                "1. Carrosserie: rouille, impacts, peinture uniforme. "
                "2. Moteur: fuites huile, fumee, bruit anormal. "
                "3. Boite de vitesses: passages fluides, pas de bruit. "
                "4. Freins: epaisseur plaquettes, disques non voiles. "
                "5. Pneus: usure uniforme, age max 5 ans. "
                "6. Interieur: climatisation, electrique, tableau de bord. "
                "7. Documents: carte grise, controle technique, historique entretien. "
                "8. Essai routier: 15-20 min minimum. "
                "Conseil: fais verifier par un mecanicien de confiance avant achat."
            )

        elif name == "rappel_entretien":
            km_actuel = inputs.get("km_actuel", 0)
            derniere = inputs.get("derniere_vidange_km", 0)
            if derniere:
                parcourus = km_actuel - derniere
                restant = 5000 - parcourus
                if restant <= 0:
                    return f"Vidange en retard de {abs(restant)} km! A faire immediatement."
                return f"Prochaine vidange dans {restant} km (a {derniere + 5000} km). Vous avez parcouru {parcourus} km depuis la derniere vidange."
            prochain = ((km_actuel // 5000) + 1) * 5000
            return f"Prochaine vidange recommandee a {prochain} km (dans {prochain - km_actuel} km)."

        elif name == "urgence_panne":
            s = inputs.get("symptome_urgent", "").lower()
            if any(k in s for k in ["fumee", "feu", "incendie", "brule"]):
                return "DANGER! Arretez immediatement, coupez le moteur, sortez du vehicule, eloignez-vous. Appelez le 14 (pompiers)."
            elif any(k in s for k in ["surchauffe", "temperature", "rouge"]):
                return "Arretez le moteur immediatement! Ne pas ouvrir le radiateur a chaud. Attendez 30 min. Verifiez le niveau liquide refroidissement froid."
            elif any(k in s for k in ["frein", "pedale", "plus de frein"]):
                return "Freins defaillants: retrogradez progressivement, utilisez le frein a main doucement, cherchez un obstacle mou pour arreter. Ne pas paniquer."
            elif any(k in s for k in ["direction", "volant", "plus de direction"]):
                return "Direction defaillante: gardez le calme, ralentissez progressivement, signalez et arretez-vous en securite."
            return "Arretez-vous en securite, mettez les feux de detresse. Appelez un depanneur ou un garage de la wilaya."

    finally:
        db.close()
    return "Information non disponible."


async def analyze_image(image_b64: str, media_type: str, user_message: str) -> str:
    try:
        content = []
        if user_message.strip():
            content.append({"type": "text", "text": user_message})
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}})
        content.append({"type": "text", "text": vision_prompt})
        response = await client.messages.create(model=CLAUDE_MODEL, max_tokens=1024, messages=[{"role": "user", "content": content}])
        return _clean(response.content[0].text)
    except Exception as e:
        print(f"Erreur vision: {e}")
        return "Desole, je n'ai pas pu analyser cette image."


async def process_message(user_message: str, session_id: str, image_b64=None, media_type=None):
    tools_triggered = []

    if image_b64:
        reply = await analyze_image(image_b64, media_type or "image/jpeg", user_message)
        return reply, ["vision_analysis"]

    msg_lower = user_message.lower().strip()

    # ETAPE 1: Detection sociale/emotionnelle
    is_social = any(kw in msg_lower for kw in _SOCIAL_KW)
    tech_kw = ["garage", "piece", "panne", "frein", "moteur", "voiture", "prix", "mecanicien", "vidange", "huile"]
    is_short_nontechnical = len(msg_lower.split()) <= 3 and not any(k in msg_lower for k in tech_kw)
    if is_social or is_short_nontechnical:
        try:
            response = await client.messages.create(
                model=CLAUDE_MODEL, max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            text = _clean("".join(b.text for b in response.content if b.type == "text"))
            return text or "Ahlan! Comment je peux t aider?", []
        except Exception as e:
            print("Erreur social:", e)
            return "Ahlan! Comment je peux t aider?", []

    # ETAPE 2: Detection ville
    detected_ville = ""
    for key, val in _VILLES_MAP.items():
        if key in msg_lower:
            detected_ville = val
            break

    # ETAPE 3: Forcer l outil garage si mot-cle garage detecte
    force_garage = any(kw in msg_lower for kw in _GARAGE_KW)
    if detected_ville and not force_garage:
        if any(k in msg_lower for k in ["mecani", "reparer", "depann", "trouver"]):
            force_garage = True

    if force_garage:
        tool_inputs = {"type_reparation": "", "ville": detected_ville}
        for kw in ["frein", "embrayage", "vidange", "distribution", "electricite",
                   "carrosserie", "peinture", "climatisation", "injection", "turbo",
                   "suspension", "geometrie", "pneu", "batterie"]:
            if kw in msg_lower:
                tool_inputs["type_reparation"] = kw
                break
        tool_result = execute_tool("trouver_garage", tool_inputs)
        tools_triggered.append("trouver_garage")
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": [{"type": "tool_use", "id": "forced_1", "name": "trouver_garage", "input": tool_inputs}]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "forced_1", "content": tool_result}]}
        ]
        try:
            response = await client.messages.create(
                model=CLAUDE_MODEL, max_tokens=1024,
                system=system_prompt, messages=messages
            )
            final_text = _clean("".join(b.text for b in response.content if b.type == "text"))
            return final_text or _clean(tool_result), tools_triggered
        except Exception as e:
            print("Erreur Anthropic forced:", e)
            return _clean(tool_result), tools_triggered

    # ETAPE 4: Flux normal Claude avec outils
    messages = [{"role": "user", "content": user_message}]
    try:
        response = await client.messages.create(
            model=CLAUDE_MODEL, max_tokens=1024,
            system=system_prompt, tools=tools, messages=messages
        )
        while response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tools_triggered.append(block.name)
                    result = execute_tool(block.name, block.input)
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            response = await client.messages.create(
                model=CLAUDE_MODEL, max_tokens=1024,
                system=system_prompt, tools=tools, messages=messages
            )
        final_text = _clean("".join(b.text for b in response.content if b.type == "text"))
        return final_text or "Desole, pas de reponse.", tools_triggered
    except Exception as e:
        print("Erreur Anthropic:", e)
        return "Desole, j ai un petit souci technique. Reessaie dans un instant!", tools_triggered
