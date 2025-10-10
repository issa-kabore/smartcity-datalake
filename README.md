# 🏙️ SmartCity - Data Platform for Urban Intelligence
**SmartCity** est un projet open-source conçu pour centraliser, traiter et visualiser les données publiques et environnementales de la ville de **Clermont-Ferrand**.  
L’objectif : créer une plateforme intelligente combinant plusieurs thématiques urbaines — air, immobilier, météo, énergie, mobilité — afin d’aider à la **prise de décision locale** et à la **sensibilisation citoyenne** autour de la qualité de vie et du développement durable.


---

## 🌐 Vision générale

> **Construire une vue intégrée de la ville**, basée sur des données réelles, fraîches et ouvertes, afin de suivre les indicateurs clés, détecter des tendances et explorer les corrélations entre les phénomènes urbains (pollution, météo, logement, énergie, etc.).

SmartCity s’articule autour de **modules thématiques** interconnectés, chacun reposant sur :
SmartCity s’articule autour de modules thématiques interconnectés, chacun reposant sur :
- 📦 **Collecte automatisée** (via Prefect ou API)
- 🗄️ **Base Supabase** pour le stockage structuré
- 📊 **Dashboards Streamlit** pour l’exploration et la visualisation
- 🧠 **Scripts Python** pour l’analyse, la modélisation et la génération d’insights

---

## ⚙️ Architecture générale

| Couche           | Technologie                     | Description |
|------------------|----------------------------------|-------------|
| Ingestion        | Prefect + API REST               | Orchestration et planification des flux de données |
| Stockage         | Supabase (PostgreSQL + storage)  | Base centralisée pour toutes les thématiques |
| Transformation   | Python + Pandas                  | Nettoyage, enrichissement et agrégation |
| Visualisation    | Streamlit                        | Dashboards interactifs et comparatifs |
| Indexation / RAG | FAISS + LLM (`sraxc`)            | Génération d’insights via IA conversationnelle |

---

## 🌍 Modules principaux

### 🫧 1. Air Quality

**Objectif :** Suivre et visualiser les concentrations de polluants sur Clermont-Ferrand.

- 📡 Données issues d'**OpenAQ (capteurs EEA)**
- 🔁 **Actualisation automatique toutes les 24h** via Prefect
- 🧾 Stockage dans la table `openaq_measurements` (Supabase)
- 🧹 **Suppression automatique** des données >30 jours via `delete_old_measurements` avec pagination


### 🌦️ 2. Climate & Weather (Coming Soon)
**Objectif :** Intégrer les conditions météorologiques (température, vent, précipitations, pression, prévisions) pour contextualiser la qualité de l’air et les autres indicateurs urbains.

- 🌡️ Données issues d'API météo ouvertes (Open-Meteo, Météo-France, etc.)
- 📅 Prévisions 7 jours
- 📈 Visualisations temporelles par variable
- 🔗 Corrélations pollution ↔ météo

### 🏠 3. Real Estate (Coming Soon)
### 🔋 4. Energy & Climate (Coming Soon)
### 🚗 5. Mobility (Coming Soon)



---
## 🗂️ Project Structure
        smartcity-datalake/
        │
        ├─ prefect_flows/               # Prefect flows : ingestion et transformation des données
        │
        ├─ smartcity/                   # Modules thématiques et outils internes
        │   ├─ air_quality/             # Scripts de nettoyage et calcul AQI
        │   ├─ weather/                 # Scripts météo (à venir)
        │   ├─ config.py                # Configuration générale (Supabase, API keys)
        │   ├─ database.py              # Connexion et utilitaires Supabase
        │   └─ utils.py                 # Fonctions utilitaires communes
        │
        ├─ streamlit_app/               # Streamlit front-end
        │   ├─ Home.py
        │   └─ pages/
        │       ├─ AirQuality.py
        │       ├─ Weather.py           # Coming soon
        │       └─ ...
        │
        ├─ tests/                       # Tests unitaires et d’intégration
        │
        ├─ requirements.txt             # Dépendances Python (inclut -e .)
        ├─ setup.py                     # Script d’installation du package local
        ├─ pyproject.toml               # Configuration moderne du package
        └─ README.md                    # Documentation principale du projet

---
## 🔗 Ressources utiles
| Ressource                                                                                           | Description                                             |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| 🌍 [OpenAQ — Données qualité de l’air](https://explore.openaq.org/?location=3624#12/45.769/3.15501) | Données publiques de la qualité de l’air (capteurs EEA) |
| ⚙️ [Prefect Documentation](https://docs.prefect.io/)                                                | Orchestration et planification des flux de données      |
| 🗄️ [Supabase Documentation](https://supabase.com/docs)                                             | Base de données PostgreSQL + stockage                   |
| 💬 [Streamlit Docs](https://docs.streamlit.io/)                                                     | Framework de visualisation et déploiement web           |
| 🧠 [FAISS Library](https://faiss.ai/)                                                               | Indexation vectorielle pour recherche et RAG            |