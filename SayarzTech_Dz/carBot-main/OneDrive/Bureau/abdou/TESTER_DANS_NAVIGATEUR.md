# 🌐 TESTER LE CHATBOT DANS VOTRE NAVIGATEUR

## ✅ C'EST PRÊT !

Une interface web complète a été créée pour tester le chatbot directement dans votre navigateur.

---

## 🚀 COMMENT TESTER (30 secondes) :

### **Étape 1 : Ouvrez votre navigateur**
Chrome, Firefox, Edge ou Safari

### **Étape 2 : Allez sur :**
```
http://localhost:8000
```

### **Étape 3 : Testez le chatbot !**
- Cliquez sur les questions exemples
- Ou tapez votre propre message
- L'IA Claude vous répondra instantanément ! 🎉

---

## 💬 EXEMPLES DE QUESTIONS À TESTER :

Cliquez directement sur les questions dans l'interface ou tapez :

1. **Diagnostic :**
   ```
   Ma Toyota Corolla fait un bruit bizarre en freinant
   ```

2. **Recherche de pièce :**
   ```
   Je cherche des plaquettes de frein avant pour Peugeot 308 2019
   ```

3. **Prix :**
   ```
   Quel est le prix d'une batterie pour Mercedes Classe A ?
   ```

4. **Stock :**
   ```
   Avez-vous des filtres à huile en stock pour Toyota ?
   ```

5. **Commande :**
   ```
   Je veux commander 2 bougies d'allumage
   ```

---

## 🎨 FONCTIONNALITÉS DE L'INTERFACE WEB :

✅ Design moderne et professionnel  
✅ Interface responsive (s'adapte à tous écrans)  
✅ Questions exemples cliquables  
✅ Indicateur de frappe quand l'IA rédige  
✅ Historique des messages avec timestamps  
✅ Couleurs différentes pour vos messages et ceux de l'IA  
✅ Scroll automatique vers le bas  
✅ Raccourci clavier : Entrée pour envoyer  

---

## 🔧 EN CAS DE PROBLÈME :

### ❌ "Page inaccessible" ou "Ce site est inaccessible"

**Solution :** Vérifiez que le backend tourne

```powershell
cd C:\Users\Roqia\OneDrive\Bureau\abdou\backend
python -m uvicorn main:app --reload --port 8000
```

Vous devez voir :
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

### ❌ "Erreur de connexion au serveur"

**Causes possibles :**
1. Le backend n'est pas lancé → Voir ci-dessus
2. Problème de clé API → Vérifiez `backend/.env`
3. Problème réseau → Redémarrez le serveur

### ❌ "Clé API invalide"

Vérifiez votre clé Anthropic dans `backend/.env` :
```
ANTHROPIC_API_KEY=sk-ant-api03-VOTRE_CLE_ICI
```

---

## 📊 AUTRES PAGES UTILES :

### **Documentation API interactive :**
```
http://localhost:8000/docs
```
- Testez tous les endpoints de l'API
- Voyez la structure des requêtes/réponses
- Parfait pour comprendre comment fonctionne le backend

### **Liste des pièces :**
```
http://localhost:8000/api/pieces
```
- Affiche toutes les pièces disponibles en JSON
- 17 pièces avec prix, stocks et références

### **Liste des véhicules :**
```
http://localhost:8000/api/vehicules
```
- Affiche les 8 véhicules du catalogue
- Marques : Toyota, Peugeot, Renault, VW, BMW, Mercedes, Audi, Citroën

---

## 🎯 ASTUCE DE PRO :

Utilisez **l'onglet "Network" (Réseau)** de votre navigateur (F12) pour voir :
- Les requêtes envoyées à l'API
- Le temps de réponse de l'IA
- Les outils utilisés par Claude (diagnostic, pièces, etc.)

---

## 🎉 VOUS Y ÊTES !

Votre chatbot automobile est **100% opérationnel dans votre navigateur**.

Amusez-vous à tester différentes questions et voyez comment l'IA Claude vous aide à diagnostiquer des pannes et trouver des pièces ! 🚗🔧

---

**Prochaine étape (optionnelle) :**  
Tester l'application mobile avec Expo Go si vous voulez une expérience smartphone.
