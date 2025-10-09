# 🏙️ SmartCity - Data Platform for Urban Intelligence
**SmartCity** est un projet open-source conçu pour centraliser, traiter et visualiser les données publiques et environnementales de la ville de **Clermont-Ferrand**.  
L’objectif : créer une plateforme intelligente combinant plusieurs thématiques urbaines — air, immobilier, météo, énergie, mobilité — afin d’aider à la **prise de décision locale** et à la **sensibilisation citoyenne** autour de la qualité de vie et du développement durable.


---

## 🌐 Vision générale

> **Construire une vue intégrée de la ville**, basée sur des données réelles, fraîches et ouvertes, afin de suivre les indicateurs clés, détecter des tendances et explorer les corrélations entre les phénomènes urbains (pollution, météo, logement, énergie, etc.).

SmartCity s’articule autour de **modules thématiques** interconnectés, chacun reposant sur :

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

- 📡 Données issues d’**OpenAQ (capteurs EEA)**
- 🔁 **Actualisation automatique toutes les 24h** via Prefect
- 🧾 Stockage dans la table `openaq_measurements` (Supabase)
- 🧹 **Suppression automatique** des données >30 jours via `delete_old_measurements` avec pagination




---
## 🗂️ Project Structure

    smartcity-datalake/
    │
    ├─ prefect_flows/               # Prefect flows : ingestion et transformation des données
    │
    ├─ smartcity/                   # Modules thématiques
    │   ├─ air_quality/             # Scripts de nettoyage et calcul AQI
    │   ├─ config.py                # Configuration générale (Supabase, API keys)
    │   ├─ database.py              # Connexion et utils Supabase
    │   └─ utils.py                 # Fonctions utilitaires communes
    │
    ├─ streamlit_app/               # Streamlit entry point
    │
    ├─ tests/                       # Tests unitaires et d’intégration
    │
    └─ README.md                    # Documentation principale du projet
