# 🚀 GUIDE RAPIDE - AutoChatbot

## ✅ Ce qui est DÉJÀ fait :

1. ✅ Backend Python installé et configuré
2. ✅ Clé API Anthropic configurée
3. ✅ Base de données créée (8 véhicules + 17 pièces)
4. ✅ Serveur backend lancé sur le port 8000
5. ✅ Application mobile React Native créée

---

## 📱 3 ÉTAPES POUR TESTER MAINTENANT :

### ÉTAPE 1 — Trouver votre IP locale (2 minutes)

Ouvrez PowerShell et tapez :
```powershell
ipconfig
```

Cherchez **Adresse IPv4** → Exemple : `192.168.1.100`

---

### ÉTAPE 2 — Modifier App.js (1 minute)

1. Ouvrez le fichier : `AutoChatbot/App.js`
2. Ligne 15, remplacez l'IP :

```javascript
// AVANT :
const API_URL = 'http://192.168.1.100:8000/api/chat';

// APRÈS (avec VOTRE IP) :
const API_URL = 'http://VOTRE_IP_TROUVEE:8000/api/chat';
```

3. Sauvegardez (Ctrl+S)

---

### ÉTAPE 3 — Installer et lancer l'app (5 minutes)

Dans PowerShell :
```powershell
cd C:\Users\Roqia\OneDrive\Bureau\abdou\AutoChatbot
npm install
npx expo start
```

✅ Un QR code va apparaître !

---

## 📲 Scanner avec votre téléphone

1. **Téléchargez "Expo Go"** :
   - iPhone : [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android : [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Scannez le QR code** avec l'app

3. **Testez le chatbot !** 🎉

---

## 💬 Exemples de messages à tester :

- "Ma Toyota Corolla fait un bruit en freinant"
- "Je cherche des plaquettes de frein pour Peugeot 308"
- "Prix d'une batterie pour Mercedes Classe A"
- "Diagnostique un problème de moteur"

---

## 🔧 Si ça ne marche pas :

### Problème : "Erreur de connexion"
✅ Vérifiez que le backend tourne toujours (Terminal 1)
✅ Vérifiez que l'IP dans App.js est correcte
✅ PC et téléphone doivent être sur le même WiFi

### Problème : "npm install échoue"
✅ Essayez : `npm install --legacy-peer-deps`

### Problème : "Clé API invalide"
✅ Vérifiez `backend/.env` avec votre clé Anthropic

---

## 📞 Besoin d'aide ?

Testez l'API dans votre navigateur :
→ http://localhost:8000/docs

---

**Projet complet : README.md**
