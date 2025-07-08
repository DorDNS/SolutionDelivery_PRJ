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

## 👥 Équipe

* Doryan Denis
* Nour Mezzi
* Thomas Fischer
* Eva Marot
* Louise Monciero
* Camille Tura-Durand

## 🚀 Lancer le projet TrashMap en local

Voici les étapes à suivre pour exécuter le projet TrashMap sur votre machine après avoir cloné ce dépôt GitHub.

### ✅ Prérequis (à faire une seule fois)

Avant de commencer, vérifiez que vous avez :

* **Node.js v18 ou supérieur** installé
  (Vous pouvez vérifier avec `node -v` dans le terminal)
* **npm** installé (inclus avec Node.js)
* Un terminal : Terminal macOS, Git Bash / PowerShell sur Windows, ou tout terminal Unix/Linux
* (Optionnel mais recommandé) **Visual Studio Code**

### 📦 Étapes après le clonage du projet

Une fois que vous avez cloné ce dépôt GitHub sur votre machine, voici ce qu’il faut faire :

**1. Ouvrez deux terminals pour gérer le backend et le frontend.**

**2. Dans votre premier terminal placez vous dans le dossier `backend`:**

```bash
cd [nom-du-projet-cloné]
cd backend
```

**2. Et créez puis activez votre environnement python `.env`:**

Pour le créer :
```bash
python3 -m venv .env
```

> Puis si vous êtes sous Windows : 
```bash
.env/Scripts/activate
```

> Sous MacOS :
```bash
source .env/bin/activate
```

**3. Toujours dans le dossier `backend` téléchargez les dépendances:**

```bash
pip install -r setup.txt
```
> Il est préférable d'opérer sous Python 3.11

**4. Enfin dans le dossier `src` lancez le serveur:**

```bash
cd src
python3 manage.py runserver
```

**5. Dans le deuxième terminal se placer dans le dossier `frontend` :**

```bash
cd [nom-du-projet-cloné]
cd frontend
```

**6. Installer les dépendances du projet :**

```bash
npm install
```

> Cela va créer automatiquement le dossier `node_modules/` (qui est ignoré par Git).

**7. (Facultatif) Copier le fichier `.env.example` si présent :**

```bash
cp .env.example .env
```

> Sinon, vous pouvez créer un fichier `.env` vide ou le configurer selon les besoins ultérieurs (actuellement pas requis pour ce projet).

**8. Lancer le serveur de développement Nuxt :**

```bash
npm run dev
```

**5. Accéder au site dans le navigateur :**

Ouvrez votre navigateur à l'adresse suivante :

```
http://localhost:3000
```

Vous verrez la page d’accueil avec l’image de fond, le titre animé, les boutons, et la section dashboard.

### ⚠️ Ce que vous n’avez pas besoin de faire :

* **Pas besoin de créer le dossier `.nuxt/` ou `.output/`** → ils sont générés automatiquement par Nuxt
* **Pas besoin de toucher à `node_modules/`** → il est généré par `npm install`
* **Pas besoin de créer des pages ou composants supplémentaires** → tout est déjà prêt

### ⛅️ Pour faire fonctionner la météo

**1. S'inscrire sur OpenWeatherMap via le lien suivant :**

[Lien d'inscription](https://home.openweathermap.org/users/sign_up)

**2. Récupérer sa clé API via le lien suivant :**

[Récupérer sa clé API](https://home.openweathermap.org/api_keys)
Elle devrait s'appeler `default`.

**3. Créer la variable pour faire fonctionner le module météo :**
* Créer un fichier `.env` dans le dossier `frontend` (à la racine)
* Copier-coller ceci dans ce fichier : `VITE_OPENWEATHER_API_KEY=`
* Après le = copiez-collez votre clé API

**L'activation de votre clé prendra un certain temps donc ne vous inquiétez pas si la météo ne s'affiche pas immédiatement, rafraichissez régulièrement la page après 20min**

## 🧠 Que contient le projet ?

* `frontend/app/pages/` : les pages Vue/Nuxt (`index.vue`, `upload.vue`)
* `frontend/app/components/` : les composants comme `Header` et `Footer`
* `frontend/app/layouts/default.vue` : le layout principal avec structure page complète
* `frontend/public/images/` : image de fond (`hero-fond.png`)
* `frontend/nuxt.config.ts` : configuration globale de Nuxt


## 📝 Licence

Projet académique réalisé dans le cadre du MasterCamp Data EFREI 2025 – **non destiné à une exploitation commerciale**.
