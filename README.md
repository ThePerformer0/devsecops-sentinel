# 🛡️ DevSecOps Sentinel — Agent SRE Autonome d'Analyse d'Incidents

**DevSecOps Sentinel** est un agent d'ingénierie de fiabilité des systèmes (Site Reliability Engineering — SRE) conçu pour automatiser l'analyse des logs, le diagnostic des causes racines (*Root Cause Analysis*) et la génération de scripts de remédiation pour les architectures microservices.

Le projet exploite **Google Agent Development Kit (ADK)**, le protocole **Model Context Protocol (MCP)** et les techniques de **Context Engineering** pour garantir des diagnostics rapides, précis et fiables.

🌐 **Démo en direct :** [DevSecOps Sentinel Live Interface](https://www.google.com/search?q=https://devsecops-sentinel.onrender.com)

---

## 🏗️ Architecture du Système

```text
+-----------------------+       Model Context Protocol      +-------------------------+
|   Google ADK Agent    | <===============================> |    MCP Log Collector    |
| (Root Cause Analysis) |           (via stdio)             | (Log Filtering & Chaos) |
+-----------------------+                                   +-------------------------+
           |                                                            |
           v                                                            v
+-----------------------+                                   +-------------------------+
| Loop Validation Agent |                                   | System Logs & Metrics   |
+-----------------------+                                   +-------------------------+

```

L'application est découpée en deux briques totalement indépendantes :

1. **L'Agent Orchestrateur (Google ADK) :** Interprète les requêtes SRE, raisonne en boucle (*ReAct* / *Loop Agent*) et valide la conformité du rapport.
2. **Le Serveur MCP (`mcp_server.py`) :** Expose les fonctionnalités système (collecte filtrée des logs, injection de pannes) sous forme d'outils standardisés via `stdio`.

---

## ✨ Fonctionnalités Clés

* **Intégration Model Context Protocol (MCP) :** Découplage strict entre la logique du LLM et les données système. L'agent interroge des outils distants via le protocole open-source MCP.
* **Context Engineering (Write / Select / Compress) :** Filtrage intelligent des logs au niveau du serveur MCP pour éliminer le bruit (`INFO`, `HEALTHCHECK`) et éviter le *Context Poisoning* ou la distraction du modèle.
* **Validation Autonome en Boucle (Loop Agent) :** Système d'auto-correction combinant un agent analyste (`LogFetcherAgent`) et un agent de contrôle qualité (`QualityChecker`) avec arrêt automatique (`exit_loop`).
* **Génération de Scripts de Remédiation :** Production automatique de commandes directement exécutables (Bash, SQL, `kubectl`) adaptées à l'incident détecté.
* **Simulation de Pannes (Chaos Engineering) :** Outil d'injection de pannes à la volée (fuite mémoire, expiration de certificat TLS, saturation de pool DB) pour tester la résilience du système.

---

## 🛠️ Stack Technique

* **Langage :** Python 3.11
* **Orchestration d'Agents :** Google Agent Development Kit (ADK)
* **Modèle de Langage :** Google Gemini 2.5 Flash
* **Protocoles & Outils :** FastMCP (Model Context Protocol)
* **Conteneurisation & Déploiement :** Docker (Linux Slim), Render (Serverless)

---

## 🚀 Installation & Exécution Locale

### Prérequis

* Python 3.10 ou supérieur
* Une clé API Google Gemini (disponible gratuitement sur [Google AI Studio](https://aistudio.google.com/))

### Étapes d'installation

1. **Cloner le dépôt Git :**
```bash
git clone https://github.com/ThePerformer0/devsecops-sentinel.git
cd devsecops-sentinel

```


2. **Créer et activer un environnement virtuel :**
* **Sous Windows (PowerShell) :**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```


* **Sous Linux / macOS :**
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Installer les dépendances :**
```bash
pip install uv
uv pip install -r requirements.txt

```


4. **Configurer les variables d'environnement :**
Créer un fichier `.env` à la racine du projet :
```env
GEMINI_API_KEY=votre_cle_api_gemini
MODEL_NAME=gemini-2.5-flash

```


5. **Lancer l'interface Web ADK :**
```bash
adk web app

```


L'application sera accessible sur `http://localhost:8000`.

---

## 🐳 Déploiement Docker

Pour conteneuriser et exécuter le projet localement avec Docker :

```bash
# Construction de l'image
docker build -t devsecops-sentinel .

# Lancement du conteneur
docker run -p 8080:8080 --env-file .env devsecops-sentinel

```

L'interface sera disponible sur `http://localhost:8080`.

---

## 🧪 Exemples d'Utilisation

Voici quelques scénarios à tester directement dans l'interface :

* **Analyse d'incident standard :**
> *"Peux-tu analyser les logs du service payment-service ?"*


* **Filtrage de contexte :**
> *"Analyse les logs du service auth-service en ne récupérant que les erreurs critiques."*


* **Chaos Engineering & Remédiation :**
> *"Injecte une panne de type memory_leak sur le service checkout-service et propose un diagnostic avec un script de correction."*



---

## 📂 Structure du Projet

```text
devsecops-sentinel/
├── app/
│   ├── __init__.py
│   └── agent.py          # Logique des agents ADK (Analyste, Validateur, Loop Agent)
├── mcp_server.py         # Serveur MCP (Collecte de logs & Injection Chaos)
├── Dockerfile            # Configuration pour conteneurisation Linux
├── requirements.txt      # Dépendances Python du projet
├── .env                  # Variables d'environnement (Clé API & Modèle)
└── README.md             # Documentation du projet

```
