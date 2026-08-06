import os
import sys
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import McpToolset, exit_loop
from mcp import StdioServerParameters

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# ---------------------------------------------------------------------------
# 1. CONFIGURATION DU CLIENT MCP (Standard Input/Output)
# ---------------------------------------------------------------------------
# On indique a l'ADK comment lancer notre serveur MCP localement
SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp_server.py"))

mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,  # Utilise l'interpréteur Python de ton venv
        args=[SERVER_PATH],      # Chemin absolu vers le serveur MCP
    )
)

# ---------------------------------------------------------------------------
# 2. AGENT INVESTIGATEUR (Appelle le serveur MCP pour récupérer les logs)
# ---------------------------------------------------------------------------
log_fetcher_agent = LlmAgent(
    name="LogFetcherAgent",
    model=MODEL_NAME,
    tools=[mcp_toolset],
    description="Récupère les logs d'un service via le serveur MCP et produit un rapport.",
    instruction=(
        "Tu es un ingénieur SRE. Lorsque l'utilisateur te demande de vérifier un service :\n"
        "1. Appelle l'outil MCP `fetch_latest_logs` avec le nom du service concerné.\n"
        "2. Analyse les logs retournés.\n"
        "3. Produis un rapport structuré en Markdown contenant :\n"
        "   - **Service analysé**\n"
        "   - **Résumé de l'incident** (1 phrase)\n"
        "   - **Cause Racine (Root Cause)**\n"
        "   - **Niveau de Sévérité** (CRITICAL, HIGH, MEDIUM, LOW)\n"
        "   - **Recommandation d'action**\n"
        "Si le service n'est pas trouvé, indique la liste des services disponibles."
    ),
    output_key="diagnostic_report",
)

# ---------------------------------------------------------------------------
# 3. AGENT DE CONTRÔLE (VALIDATEUR)
# ---------------------------------------------------------------------------
quality_checker = LlmAgent(
    name="QualityChecker",
    model=MODEL_NAME,
    tools=[exit_loop],
    description="Vérifie la qualité du rapport d'analyse.",
    instruction=(
        "Examine le rapport dans 'diagnostic_report'.\n"
        "Vérifie qu'il contient la Cause Racine et la Sévérité.\n"
        "Si TOUT est correct et complet, appelle l'outil `exit_loop` et réponds strictement : OK\n"
        "Sinon, réponds : RETRY"
    ),
)

# ---------------------------------------------------------------------------
# 4. LOOP AGENT
# ---------------------------------------------------------------------------
robust_log_analyzer = LoopAgent(
    name="RobustLogAnalyzer",
    sub_agents=[log_fetcher_agent, quality_checker],
    max_iterations=3,
)

root_agent = robust_log_analyzer