# 🧠 Plateforme intelligente de suivi des poubelles – Wild Dump Prevention (WDP)

## 📌 Contexte

Face à l’absence de données précises sur les déchets abandonnés et l’inefficacité des méthodes actuelles de prévention, le projet **WDP** (Wild Dump Prevention) propose une **solution numérique innovante** pour :

- Détecter automatiquement l’état des poubelles publiques (pleine, vide) à partir d’images,
- Identifier les zones à risque de débordement,
- Aider les collectivités à améliorer leur gestion des déchets et prévenir les dépôts sauvages.

Ce projet s’inscrit dans une logique **AI for Good** et de **Green IT**, visant un impact environnemental et sociétal positif.

## 🎯 Objectifs

- Développement d’une **plateforme web** pour la détection automatique d’ordures via des images.
- Mise en place d’un système de **classification sans IA** basé sur des règles conditionnelles.
- Visualisation des données via un **tableau de bord interactif**.
- Suivi de l’état des poubelles sur le territoire (cartographie dynamique).
- Intégration de bonnes pratiques en **éco-conception** et **gestion des risques**.

## 🧩 Fonctionnalités principales

### 🖼️ 1. Gestion des images
- Upload d’images (utilisateur, agent, caméra embarquée),
- Annotation manuelle (pleine / vide),
- Visualisation directe sur l’interface.

### 📐 2. Extraction automatique de caractéristiques
- Taille du fichier, dimensions, couleur moyenne,
- Histogramme, contraste, contours (OpenCV),
- Stockage en base avec métadonnées (date, localisation, etc.).

### ⚙️ 3. Classification par règles
- Système basé sur des seuils configurables (ex. couleur moyenne, taille),
- Application automatique d’un label « pleine » ou « vide ».

### 📊 4. Tableau de bord interactif
- Statistiques globales : % d’images pleines, localisation, dates, etc.
- Graphiques via Chart.js et Matplotlib,
- Cartographie dynamique des zones à risque.

### ♻️ 5. Éco-conception (RGESN)
- Intégration des recommandations du Référentiel Général d'Écoconception,
- Réduction des impacts : poids des images, nombre de requêtes, hébergement durable.

### ⚠️ 6. Évaluation des risques
- Analyse des risques liés à la qualité des images, l’annotation manuelle, la variabilité technique des utilisateurs, etc.
- Mesures d’atténuation prévues (prévisualisation, contrôle qualité, documentation).

## 🧑‍💻 Technologies utilisées

| Côté | Technologies |
|------|--------------|
| Back-end | Python, Flask/Django, SQLite ou PostgreSQL |
| Traitement image | Pillow, OpenCV, os, shutil |
| Front-end | HTML, CSS, Bootstrap, JavaScript, Chart.js |
| Visualisation | matplotlib, Chart.js |
| Hébergement | local / cloud écoresponsable recommandé |
| Conformité Green IT | RGESN, grille d’impact, pratiques écoresponsables |

## 🧱 Structure du projet

```
📦 SolutionDelivery_PRJ/
│
├── app/                    # 📌 Application principale (code Flask/Django)
│   ├── routes/             # Endpoints (upload, annotation, dashboard…)
│   ├── templates/          # Fichiers HTML (Jinja)
│   ├── static/             # Fichiers statiques (CSS, JS, images du front)
│   ├── logic/              # Fonctions métier : classification, feature extraction
│   └── main.py             # Lancement du serveur web
│
├── data/                   # 📁 Données locales
│   ├── raw/                # Images originales (uploadées)
│   ├── processed/          # Images annotées / traitées
│   ├── features.csv        # Données extraites par image
│   └── db.sqlite3          # Base SQLite
│
├── scripts/                # 🛠️ Scripts indépendants
│   ├── extract_features.py # Extraction de caractéristiques visuelles
│   ├── classify_rules.py   # Règles de classification automatique
│   ├── clean_db.py         # Nettoyage, réinitialisation de la base
│   └── ...
│
├── dashboard/              # 📊 Visualisations et graphes
│   ├── stats.py            # Stats matplotlib
│   └── dashboard.html      # Tableau de bord (front)
│
├── tests/                  # ✅ Tests unitaires (si implémentés)
│   ├── test_upload.py
│   └── test_classification.py
│
├── docs/                   # 📚 Documentation du projet
│   ├── README.md           # Présentation du projet
│   ├── Rapport_final.pdf   # Rapport technique (rendu)
│   ├── Evaluation_des_risques_final.pdf
│   ├── Questionnaire_ecoconception.pdf
│   └── Grille_impacts_projets.pdf
│
├── requirements.txt        # 📦 Dépendances Python
├── .gitignore              # 🧼 Fichiers à ignorer (base, images…)
└── README.md               # 📝 Présentation principale du dépôt
````

## ✅ Exécution locale

```bash
# 1. Cloner le repo
git clone https://github.com/DorDNS/SolutionDelivery_PRJ
cd wdp-platform

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application (ex: Flask)
python app/main.py
````

## 📚 Livrables attendus

* Plateforme fonctionnelle (back + front),
* Base de données d’images et annotations,
* Rapport technique :

  * Architecture de la solution,
  * Fonctionnement des extractions et règles,
  * Évaluation des risques,
  * Justification Green IT,
  * Captures du tableau de bord.

## 👥 Équipe

* Doryan Denis
* Nour Mezzi
* Thomas Fischer
* Eva Marot
* Louise Monciero
* Camille Tura-Durand

## 📝 Licence

Projet académique réalisé dans le cadre du MasterCamp Data EFREI 2025 – **non destiné à une exploitation commerciale**.

## 🌿 Démarche écoresponsable

Ce projet intègre une **démarche Green IT** selon les référentiels du [RGESN](https://ecoresponsable.numerique.gouv.fr/) :

* Architecture logicielle légère,
* Limitation des requêtes, pagination,
* Compression des images,
* Hébergement durable privilégié,
* Documentation des impacts via grille et questionnaire d’écoconception.

## 📎 Liens utiles

* Rapport complet : `docs/Master_camp-Data_Final.pdf`
* Évaluation des risques : `docs/Evaluation_des_risques_final.pdf`
* Questionnaire RGESN : `docs/Questionnaire_d_ecoconception.pdf`
* Grille d’impact : `docs/Grille_des_impacts_projets.pdf`
