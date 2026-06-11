from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models

Base.metadata.create_all(bind=engine)

VEHICULES = [
    {"marque": "Renault", "modele": "Symbol", "annee": 2018, "immatriculation": "16-ALG-001"},
    {"marque": "Renault", "modele": "Clio 4", "annee": 2020, "immatriculation": "16-ALG-002"},
    {"marque": "Peugeot", "modele": "301", "annee": 2019, "immatriculation": "16-ALG-003"},
    {"marque": "Peugeot", "modele": "208", "annee": 2021, "immatriculation": "16-ALG-004"},
    {"marque": "Toyota", "modele": "Yaris", "annee": 2020, "immatriculation": "16-ALG-005"},
    {"marque": "Toyota", "modele": "Corolla", "annee": 2022, "immatriculation": "16-ALG-006"},
    {"marque": "Hyundai", "modele": "Elantra", "annee": 2019, "immatriculation": "16-ALG-007"},
    {"marque": "Hyundai", "modele": "i10", "annee": 2021, "immatriculation": "16-ALG-008"},
    {"marque": "Kia", "modele": "Picanto", "annee": 2020, "immatriculation": "16-ALG-009"},
    {"marque": "Kia", "modele": "Sportage", "annee": 2021, "immatriculation": "16-ALG-010"},
    {"marque": "Dacia", "modele": "Logan", "annee": 2019, "immatriculation": "16-ALG-011"},
    {"marque": "Dacia", "modele": "Sandero", "annee": 2022, "immatriculation": "16-ALG-012"},
    {"marque": "Volkswagen", "modele": "Polo", "annee": 2020, "immatriculation": "16-ALG-013"},
    {"marque": "Volkswagen", "modele": "Golf 7", "annee": 2018, "immatriculation": "16-ALG-014"},
    {"marque": "Suzuki", "modele": "Swift", "annee": 2021, "immatriculation": "16-ALG-015"},
]

# Prix en Dinars Algériens (DZD)
PIECES = [
    # ===== FREINAGE =====
    {"nom": "Plaquettes de frein avant", "reference": "FRN-001", "categorie": "Freinage",
     "description": "Plaquettes avant compatibles Renault Symbol/Clio/Logan. Matériau semi-métallique, résistance à la chaleur élevée. Durée de vie ~40 000 km. Remplacement recommandé quand épaisseur < 3mm.", "prix": 2800, "stock": 25},
    {"nom": "Plaquettes de frein arrière", "reference": "FRN-002", "categorie": "Freinage",
     "description": "Plaquettes arrière universelles Peugeot/Dacia. Frein à tambour ou disque selon modèle. Vérifier le témoin d'usure avant remplacement.", "prix": 2200, "stock": 20},
    {"nom": "Disque de frein avant (paire)", "reference": "FRN-003", "categorie": "Freinage",
     "description": "Disques ventilés avant pour Toyota Yaris/Corolla. Diamètre 256mm. Toujours remplacer par paire. Contrôler l'épaisseur minimale gravée sur le disque.", "prix": 6500, "stock": 12},
    {"nom": "Disque de frein arrière (paire)", "reference": "FRN-004", "categorie": "Freinage",
     "description": "Disques pleins arrière Hyundai Elantra/i10. Diamètre 234mm. Inspecter les rainures et voilage avant montage.", "prix": 5200, "stock": 10},
    {"nom": "Tambour de frein arrière", "reference": "FRN-005", "categorie": "Freinage",
     "description": "Tambour arrière Dacia Logan/Sandero. Remplace le système à tambour. Vérifier le diamètre intérieur max indiqué sur le tambour.", "prix": 3800, "stock": 8},
    {"nom": "Maître-cylindre de frein", "reference": "FRN-006", "categorie": "Freinage",
     "description": "Maître-cylindre double circuit. Symptôme de défaillance: pédale molle ou qui descend. Purger le circuit après remplacement.", "prix": 4500, "stock": 6},
    {"nom": "Étrier de frein avant gauche", "reference": "FRN-007", "categorie": "Freinage",
     "description": "Étrier avant gauche Volkswagen Polo/Golf. Vérifier les pistons et joints. Nettoyer les glissières avant montage.", "prix": 5800, "stock": 5},

    # ===== MOTEUR =====
    {"nom": "Filtre à huile moteur", "reference": "MOT-001", "categorie": "Moteur",
     "description": "Filtre à huile universel (filetage M20x1.5). Compatible la plupart des moteurs 1.2 à 1.6L. Changer à chaque vidange (5 000 à 10 000 km selon huile utilisée).", "prix": 650, "stock": 50},
    {"nom": "Filtre à air moteur", "reference": "MOT-002", "categorie": "Moteur",
     "description": "Filtre à air papier haute filtration. Remplacer tous les 15 000 km ou si encrassé. Un filtre bouché augmente la consommation de carburant.", "prix": 900, "stock": 40},
    {"nom": "Bougie d'allumage (x4)", "reference": "MOT-003", "categorie": "Moteur",
     "description": "Bougies iridium longue durée (jeu de 4). Écartement 1.0mm. Symptômes de bougies usées: démarrage difficile, à-coups, surconsommation. Changer tous les 30 000 km.", "prix": 3200, "stock": 30},
    {"nom": "Courroie de distribution + kit", "reference": "MOT-004", "categorie": "Moteur",
     "description": "Kit complet: courroie + galet tendeur + pompe à eau. CRITIQUE: rupture = casse moteur garantie. Changer tous les 60 000 km ou 5 ans. Opération à confier à un professionnel.", "prix": 8500, "stock": 8},
    {"nom": "Joint de culasse", "reference": "MOT-005", "categorie": "Moteur",
     "description": "Joint de culasse multicouches acier. Symptômes de fuite: fumée blanche, huile émulsionnée (couleur café au lait), surchauffe. Vérifier planéité culasse avant montage.", "prix": 3500, "stock": 7},
    {"nom": "Pompe à eau", "reference": "MOT-006", "categorie": "Moteur",
     "description": "Pompe à eau mécanique entraînée par courroie. Remplacer en même temps que la courroie de distribution. Symptôme: fuite de liquide de refroidissement sous le moteur.", "prix": 2800, "stock": 12},
    {"nom": "Thermostat moteur", "reference": "MOT-007", "categorie": "Moteur",
     "description": "Thermostat 87°C avec joint. Symptôme de panne: moteur qui chauffe trop vite (thermostat bloqué fermé) ou qui n'atteint pas la température (bloqué ouvert).", "prix": 1200, "stock": 18},
    {"nom": "Sonde de température moteur", "reference": "MOT-008", "categorie": "Moteur",
     "description": "Capteur température liquide de refroidissement. Provoque allumage du voyant température ou lecture erronée au tableau de bord.", "prix": 950, "stock": 15},
    {"nom": "Vanne EGR", "reference": "MOT-009", "categorie": "Moteur",
     "description": "Vanne de recirculation des gaz d'échappement. Encrassement fréquent sur diesel. Symptômes: perte de puissance, fumée noire, voyant moteur allumé.", "prix": 7200, "stock": 4},

    # ===== TRANSMISSION =====
    {"nom": "Kit embrayage complet", "reference": "TRN-001", "categorie": "Transmission",
     "description": "Kit 3 pièces: disque + mécanisme + butée. Compatible Renault/Dacia 1.5 dCi. Symptômes d'usure: patinage, pédale dure, bruit au démarrage. Opération lourde, prévoir 4-6h de main d'œuvre.", "prix": 18500, "stock": 5},
    {"nom": "Disque d'embrayage seul", "reference": "TRN-002", "categorie": "Transmission",
     "description": "Disque d'embrayage Ø215mm. Remplacer si garnitures usées ou huile dessus. Vérifier le volant moteur en même temps.", "prix": 6500, "stock": 8},
    {"nom": "Roulement de roue avant", "reference": "TRN-003", "categorie": "Transmission",
     "description": "Roulement à billes avant (moyeu). Symptôme: bruit de roulement qui augmente avec la vitesse, vibrations. Tester en faisant des zigzags: le bruit change de côté.", "prix": 2200, "stock": 20},
    {"nom": "Roulement de roue arrière", "reference": "TRN-004", "categorie": "Transmission",
     "description": "Roulement arrière universel. Même diagnostic que l'avant. Remplacer par paire si kilométrage élevé.", "prix": 1900, "stock": 18},
    {"nom": "Rotule de direction inférieure", "reference": "TRN-005", "categorie": "Transmission",
     "description": "Rotule de triangle inférieur. Symptômes: bruit de claquement dans les virages ou sur dos d'âne, usure irrégulière des pneus. Contrôle géométrie obligatoire après remplacement.", "prix": 1800, "stock": 15},
    {"nom": "Biellette de barre stabilisatrice", "reference": "TRN-006", "categorie": "Transmission",
     "description": "Biellette anti-roulis. Symptôme classique: bruit de claquement sur les bosses, surtout à basse vitesse. Pièce peu chère, souvent négligée.", "prix": 850, "stock": 25},
    {"nom": "Soufflet de cardan (paire)", "reference": "TRN-007", "categorie": "Transmission",
     "description": "Soufflets de transmission intérieur+extérieur. Si soufflet déchiré: graisse projetée, cardan qui s'use rapidement. Remplacer dès que déchirure visible.", "prix": 1500, "stock": 20},

    # ===== ÉLECTRICITÉ =====
    {"nom": "Batterie 60Ah 12V", "reference": "ELC-001", "categorie": "Électricité",
     "description": "Batterie plomb-acide 60Ah 540A. Durée de vie 3-5 ans. Symptômes de faiblesse: démarrage lent, phares qui faiblissent. Tester avec voltmètre: 12.6V = pleine charge, <12V = à changer.", "prix": 9500, "stock": 15},
    {"nom": "Batterie 45Ah 12V (petite citadine)", "reference": "ELC-002", "categorie": "Électricité",
     "description": "Batterie 45Ah pour Hyundai i10, Kia Picanto, Suzuki Swift. Légère et compacte. Même diagnostic que la 60Ah.", "prix": 7200, "stock": 12},
    {"nom": "Alternateur 90A reconditionné", "reference": "ELC-003", "categorie": "Électricité",
     "description": "Alternateur reconditionné 90A. Symptômes de panne: voyant batterie allumé, batterie qui se décharge, phares qui clignotent. Tester: moteur tournant, tension doit être 13.8-14.4V.", "prix": 12000, "stock": 6},
    {"nom": "Démarreur reconditionné", "reference": "ELC-004", "categorie": "Électricité",
     "description": "Démarreur reconditionné universel. Symptômes: cliquetis au démarrage, moteur qui ne tourne pas, bruit de frottement. Vérifier aussi le solénoïde.", "prix": 9800, "stock": 5},
    {"nom": "Bobine d'allumage", "reference": "ELC-005", "categorie": "Électricité",
     "description": "Bobine crayon individuelle (par cylindre). Symptômes: raté d'allumage, voyant moteur clignotant, perte de puissance sur un cylindre. Tester en permutant les bobines.", "prix": 2800, "stock": 10},
    {"nom": "Capteur ABS roue avant", "reference": "ELC-006", "categorie": "Électricité",
     "description": "Capteur de vitesse de roue pour système ABS. Voyant ABS allumé = capteur défaillant ou câble coupé. Nettoyer la cible magnétique avant de remplacer.", "prix": 2200, "stock": 12},
    {"nom": "Sonde lambda (capteur O2)", "reference": "ELC-007", "categorie": "Électricité",
     "description": "Sonde lambda amont universelle. Symptômes de panne: surconsommation, voyant moteur, mauvaise combustion. Durée de vie ~80 000 km.", "prix": 4500, "stock": 8},

    # ===== REFROIDISSEMENT =====
    {"nom": "Radiateur de refroidissement", "reference": "REF-001", "categorie": "Refroidissement",
     "description": "Radiateur aluminium/plastique. Symptômes de fuite: flaque de liquide vert/rose sous le véhicule, surchauffe. Vérifier aussi les durites et le bouchon de radiateur.", "prix": 11000, "stock": 6},
    {"nom": "Liquide de refroidissement 5L", "reference": "REF-002", "categorie": "Refroidissement",
     "description": "Liquide de refroidissement concentré (diluer 50/50 avec eau distillée). Protection jusqu'à -35°C. Changer tous les 2 ans. Ne jamais ouvrir le bouchon moteur chaud.", "prix": 1800, "stock": 30},
    {"nom": "Durite supérieure radiateur", "reference": "REF-003", "categorie": "Refroidissement",
     "description": "Durite haute (entre moteur et radiateur). Vérifier les durites à chaque vidange: durcissement, craquelures, gonflement = remplacement nécessaire.", "prix": 950, "stock": 20},
    {"nom": "Ventilateur électrique radiateur", "reference": "REF-004", "categorie": "Refroidissement",
     "description": "Moto-ventilateur de refroidissement. Symptôme de panne: surchauffe en ville (à l'arrêt), fonctionne bien sur route. Vérifier le fusible et le relais avant de remplacer.", "prix": 5500, "stock": 7},

    # ===== DIRECTION =====
    {"nom": "Crémaillère de direction", "reference": "DIR-001", "categorie": "Direction",
     "description": "Crémaillère direction assistée hydraulique. Symptômes: jeu au volant, bruit de claquement, fuite d'huile de direction. Contrôle géométrie obligatoire après remplacement.", "prix": 22000, "stock": 3},
    {"nom": "Pompe de direction assistée", "reference": "DIR-002", "categorie": "Direction",
     "description": "Pompe hydraulique direction assistée. Symptômes: volant dur, bruit de pompe (sifflement), fuite d'huile. Vérifier le niveau d'huile de direction en premier.", "prix": 14000, "stock": 4},
    {"nom": "Huile de direction assistée 1L", "reference": "DIR-003", "categorie": "Direction",
     "description": "Huile hydraulique pour direction assistée. Vérifier le niveau régulièrement. Une baisse de niveau indique une fuite à localiser.", "prix": 650, "stock": 25},

    # ===== SUSPENSION =====
    {"nom": "Amortisseur avant (l'unité)", "reference": "SUS-001", "categorie": "Suspension",
     "description": "Amortisseur avant à gaz. Toujours remplacer par paire (gauche + droite). Symptômes d'usure: rebonds excessifs, nez qui plonge au freinage, bruit de choc. Test: appuyer sur le capot et relâcher, doit s'arrêter en 1 rebond.", "prix": 5500, "stock": 10},
    {"nom": "Amortisseur arrière (l'unité)", "reference": "SUS-002", "categorie": "Suspension",
     "description": "Amortisseur arrière. Même principe que l'avant. Symptôme spécifique: arrière qui rebondit sur les bosses, instabilité en virage.", "prix": 4200, "stock": 12},
    {"nom": "Ressort de suspension avant", "reference": "SUS-003", "categorie": "Suspension",
     "description": "Ressort hélicoïdal avant. Remplacer si cassé ou affaissé (véhicule penché d'un côté). Toujours remplacer par paire.", "prix": 3200, "stock": 8},
    {"nom": "Silent-bloc de triangle", "reference": "SUS-004", "categorie": "Suspension",
     "description": "Silentbloc caoutchouc-métal pour triangle de suspension. Symptômes d'usure: bruit de caoutchouc, imprécision de direction, usure irrégulière des pneus.", "prix": 1200, "stock": 20},

    # ===== ÉCHAPPEMENT =====
    {"nom": "Pot d'échappement arrière", "reference": "ECH-001", "categorie": "Échappement",
     "description": "Silencieux arrière universel. Symptômes de fuite: bruit de pétarade, odeur de gaz dans l'habitacle (DANGEREUX - CO). Vérifier aussi les joints et colliers.", "prix": 6500, "stock": 8},
    {"nom": "Catalyseur", "reference": "ECH-002", "categorie": "Échappement",
     "description": "Pot catalytique. Symptômes de panne: voyant moteur, perte de puissance, odeur d'œuf pourri. Durée de vie ~150 000 km si entretien correct.", "prix": 18000, "stock": 3},
    {"nom": "Flexible d'échappement", "reference": "ECH-003", "categorie": "Échappement",
     "description": "Flexible métallique anti-vibrations. Souvent percé sur les vieilles voitures. Symptôme: bruit de souffle ou de pétarade sous le véhicule.", "prix": 2200, "stock": 15},

    # ===== CARROSSERIE =====
    {"nom": "Pare-brise (verre feuilleté)", "reference": "CAR-001", "categorie": "Carrosserie",
     "description": "Pare-brise feuilleté avec couche anti-UV. Toute fissure dans le champ de vision du conducteur = contrôle technique refusé. Pose par professionnel recommandée.", "prix": 15000, "stock": 5},
    {"nom": "Phare avant complet (LED)", "reference": "CAR-002", "categorie": "Carrosserie",
     "description": "Optique avant LED. Vérifier le réglage des phares après remplacement (éblouissement des autres conducteurs = infraction).", "prix": 12000, "stock": 4},
    {"nom": "Rétroviseur extérieur électrique", "reference": "CAR-003", "categorie": "Carrosserie",
     "description": "Rétroviseur électrique avec dégivrage. Vérifier le connecteur électrique avant de remplacer (souvent juste un câble débranché).", "prix": 4800, "stock": 8},
    {"nom": "Essuie-glaces avant (paire)", "reference": "CAR-004", "categorie": "Carrosserie",
     "description": "Balais essuie-glaces sans armature 600/400mm. Changer tous les ans ou dès que des traces restent sur le pare-brise. Lever les balais en hiver pour éviter le gel.", "prix": 1200, "stock": 35},

    # ===== CONSOMMABLES =====
    {"nom": "Huile moteur 5W30 5L (synthétique)", "reference": "CON-001", "categorie": "Consommables",
     "description": "Huile moteur synthétique 5W30. Vidange tous les 10 000 km avec cette huile. Vérifier le niveau tous les 1 000 km. Niveau bas = usure moteur accélérée.", "prix": 3200, "stock": 40},
    {"nom": "Huile moteur 15W40 5L (minérale)", "reference": "CON-002", "categorie": "Consommables",
     "description": "Huile minérale 15W40 pour vieux moteurs. Vidange tous les 5 000 km. Adaptée aux moteurs à fort kilométrage qui consomment de l'huile.", "prix": 1800, "stock": 45},
    {"nom": "Filtre à carburant diesel", "reference": "CON-003", "categorie": "Consommables",
     "description": "Filtre gasoil avec purge d'eau. Changer tous les 30 000 km. Un filtre bouché provoque perte de puissance et difficultés de démarrage à froid.", "prix": 1500, "stock": 25},
    {"nom": "Filtre à carburant essence", "reference": "CON-004", "categorie": "Consommables",
     "description": "Filtre essence inline. Changer tous les 30 000 km. Souvent oublié lors des entretiens.", "prix": 900, "stock": 20},
    {"nom": "Liquide de frein DOT4 500ml", "reference": "CON-005", "categorie": "Consommables",
     "description": "Liquide de frein DOT4. Changer tous les 2 ans (absorbe l'humidité). Ne jamais mélanger DOT3 et DOT5. Attention: corrosif pour la peinture.", "prix": 750, "stock": 30},
]


FOURNISSEURS = [
    # === AÏN MLILA ===
    {"nom": "Pièces Auto Brahim", "telephone": "0770 12 34 56", "adresse": "Rue Principale, centre-ville", "ville": "Aïn Mlila", "specialite": "Freinage, Moteur, Consommables"},
    {"nom": "Garage & Pièces Messaoud", "telephone": "0661 23 45 67", "adresse": "Route de Constantine, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Pièces Renault, Peugeot, Dacia"},
    {"nom": "Auto Pièces El Wiam", "telephone": "0550 34 56 78", "adresse": "Marché couvert, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Électricité auto, Batteries, Alternateurs"},
    {"nom": "Pièces Détachées Kamel", "telephone": "0790 45 67 89", "adresse": "Zone commerciale, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Suspension, Direction, Transmission"},
    {"nom": "Grossiste Auto Nordine", "telephone": "0662 56 78 90", "adresse": "Rue du 1er Novembre, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Toutes marques, Pièces d'origine et adaptables"},
    {"nom": "Pièces Japonaises Youcef", "telephone": "0555 67 89 01", "adresse": "Près de la gare routière, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Toyota, Hyundai, Kia, Suzuki"},
    {"nom": "Auto Pièces Rachid", "telephone": "0771 78 90 12", "adresse": "Boulevard Zighoud Youcef, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Carrosserie, Vitrage, Essuie-glaces"},

    # === OUM EL BOUAGHI ===
    {"nom": "Pièces Auto Centrale OEB", "telephone": "0699 89 01 23", "adresse": "Rue Larbi Ben M'hidi, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Toutes marques, Pièces d'origine"},
    {"nom": "Garage Pièces Hocine", "telephone": "0770 90 12 34", "adresse": "Route nationale 10, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Moteur, Distribution, Embrayage"},
    {"nom": "Auto Pièces El Baraka", "telephone": "0661 01 23 45", "adresse": "Marché hebdomadaire, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Freinage, Suspension, Amortisseurs"},
    {"nom": "Électricité Auto Sofiane", "telephone": "0550 12 34 56", "adresse": "Cité AADL, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Électricité, Diagnostic OBD, Capteurs"},
    {"nom": "Pièces Européennes Tarek", "telephone": "0790 23 45 67", "adresse": "Zone industrielle, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Volkswagen, Peugeot, Renault, Citroën"},
    {"nom": "Grossiste Pneus & Pièces Amar", "telephone": "0662 34 56 78", "adresse": "Route de Khenchela, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Pneus, Jantes, Roulements, Rotules"},
]

GARAGES = [
    # === AÏN MLILA ===
    {"nom": "Garage Mécanique Salah", "telephone": "0770 11 22 33", "adresse": "Rue des Frères Bouadma, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Mécanique générale, Vidange, Distribution"},
    {"nom": "Garage Électricité Auto Hamza", "telephone": "0661 22 33 44", "adresse": "Cité des 500 logements, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Électricité, Diagnostic, Climatisation"},
    {"nom": "Garage Freinage & Suspension Bilal", "telephone": "0550 33 44 55", "adresse": "Route de Oum El Bouaghi, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Freinage, Suspension, Géométrie"},
    {"nom": "Carrosserie Peinture Mourad", "telephone": "0790 44 55 66", "adresse": "Zone artisanale, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Carrosserie, Peinture, Débosselage"},
    {"nom": "Garage Toutes Marques Farid", "telephone": "0662 55 66 77", "adresse": "Centre-ville, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Mécanique générale, Embrayage, Boîte de vitesses"},
    {"nom": "Garage Climatisation Auto Walid", "telephone": "0555 66 77 88", "adresse": "Rue Didouche Mourad, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Climatisation, Électricité, Diagnostic OBD"},
    {"nom": "Garage Rapide Lamine", "telephone": "0771 77 88 99", "adresse": "Près du lycée, Aïn Mlila", "ville": "Aïn Mlila", "specialite": "Vidange rapide, Filtres, Bougies, Freins"},

    # === OUM EL BOUAGHI ===
    {"nom": "Garage Central OEB Hassen", "telephone": "0699 88 99 00", "adresse": "Avenue de l'ALN, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Mécanique générale, Toutes marques"},
    {"nom": "Garage Diesel Spécialiste Riad", "telephone": "0770 99 00 11", "adresse": "Route de Aïn Mlila, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Moteurs diesel, Injection, Turbo"},
    {"nom": "Garage Électronique Auto Nassim", "telephone": "0661 00 11 22", "adresse": "Cité universitaire, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Diagnostic électronique, Calculateurs, ABS"},
    {"nom": "Garage Transmission Djamel", "telephone": "0550 11 22 33", "adresse": "Zone industrielle, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Boîte de vitesses, Embrayage, Cardans"},
    {"nom": "Carrosserie Moderne Samir", "telephone": "0790 22 33 44", "adresse": "Rue Benchergui, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Carrosserie, Peinture, Pare-brise"},
    {"nom": "Garage Géométrie & Équilibrage Zine", "telephone": "0662 33 44 55", "adresse": "Boulevard de la République, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Géométrie, Équilibrage, Pneus, Suspension"},
    {"nom": "Garage Climatisation Mehdi", "telephone": "0555 44 55 66", "adresse": "Cité OPGI, Oum El Bouaghi", "ville": "Oum El Bouaghi", "specialite": "Climatisation, Recharge gaz, Électricité"},

    # === AÏN BEIDA ===
    {"nom": "RV Motor", "telephone": "0770 55 66 77", "adresse": "Route nationale, Aïn Beida", "ville": "Aïn Beida", "specialite": "Mécanique générale, Moteur, Distribution, Toutes marques"},
    {"nom": "Revix Auto", "telephone": "0661 66 77 88", "adresse": "Centre-ville, Aïn Beida", "ville": "Aïn Beida", "specialite": "Révision complète, Vidange, Freinage, Suspension"},
    {"nom": "WR Auto Service", "telephone": "0550 77 88 99", "adresse": "Zone commerciale, Aïn Beida", "ville": "Aïn Beida", "specialite": "Mécanique, Électricité, Diagnostic OBD, Climatisation"},
    {"nom": "Service Rapide 911 - Nabile & Rassim Ibrahim", "telephone": "0790 88 99 00", "adresse": "Rue principale, Aïn Beida", "ville": "Aïn Beida", "specialite": "Dépannage rapide, Freins, Vidange express, Urgences"},
    {"nom": "Garage Rassim", "telephone": "0662 99 00 11", "adresse": "Cité des martyrs, Aïn Beida", "ville": "Aïn Beida", "specialite": "Mécanique générale, Embrayage, Boîte de vitesses, Carrosserie"},

    # === AÏN FAKROUN ===
    {"nom": "Garage Mécanique Centrale Ain Fakroun", "telephone": "0555 00 11 22", "adresse": "Route de Oum El Bouaghi, Aïn Fakroun", "ville": "Aïn Fakroun", "specialite": "Mécanique générale, Toutes marques"},
    {"nom": "Garage Électricité Auto Ain Fakroun", "telephone": "0771 11 22 33", "adresse": "Centre-ville, Aïn Fakroun", "ville": "Aïn Fakroun", "specialite": "Électricité, Diagnostic, Batterie, Alternateur"},
    {"nom": "Garage Freinage Suspension Ain Fakroun", "telephone": "0699 22 33 44", "adresse": "Zone artisanale, Aïn Fakroun", "ville": "Aïn Fakroun", "specialite": "Freinage, Suspension, Géométrie, Amortisseurs"},
    {"nom": "Carrosserie Peinture Ain Fakroun", "telephone": "0770 33 44 55", "adresse": "Rue des ateliers, Aïn Fakroun", "ville": "Aïn Fakroun", "specialite": "Carrosserie, Peinture, Débosselage, Pare-brise"},
]


def seed_database():
    db = SessionLocal()
    try:
        if db.query(models.Piece).count() > 0:
            print("✅ Base de données déjà initialisée.")
            return

        print("🌱 Initialisation de la base de données...")

        vehicules = []
        for v in VEHICULES:
            vehicule = models.Vehicule(**v)
            db.add(vehicule)
            vehicules.append(vehicule)
        db.commit()
        print(f"✅ {len(vehicules)} véhicules créés")

        pieces = []
        for p in PIECES:
            piece = models.Piece(
                nom=p["nom"],
                reference=p["reference"],
                description=p["description"],
                prix=p["prix"],
                stock=p["stock"],
            )
            db.add(piece)
            pieces.append(piece)
        db.commit()
        print(f"✅ {len(pieces)} pièces créées")

        fournisseurs = []
        for f in FOURNISSEURS:
            fournisseur = models.Fournisseur(**f)
            db.add(fournisseur)
            fournisseurs.append(fournisseur)
        db.commit()
        print(f"✅ {len(fournisseurs)} fournisseurs créés")

        garages = []
        for g in GARAGES:
            garage = models.Garage(**g)
            db.add(garage)
            garages.append(garage)
        db.commit()
        print(f"✅ {len(garages)} garages créés")

        print(f"\n🎉 Base initialisée: {len(vehicules)} véhicules, {len(pieces)} pièces, {len(fournisseurs)} fournisseurs, {len(garages)} garages")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
