import os
import sys
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import McpToolset, exit_loop
from mcp import StdioServerParameters

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp_server.py"))

mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=[SERVER_PATH],
    )
)

log_fetcher_agent = LlmAgent(
    name="LogFetcherAgent",
    model=MODEL_NAME,
    tools=[mcp_toolset],
    description="Récupère les logs, analyse les incidents et génère des remédiations SRE.",
    instruction=(
        "Tu es un ingénieur SRE (Site Reliability Engineer) Senior.\n"
        "Lorsqu'on te demande d'analyser un service ou d'injecter une panne :\n"
        "1. Interroge le serveur MCP pour obtenir les logs ou effectuer l'injection.\n"
        "2. Produis un rapport d'incident complet en Markdown :\n"
        "   - **Service & Statut**\n"
        "   - **Cause Racine (Root Cause)**\n"
        "   - **Niveau de Sévérité & Impact SLA** (Estimé : CRITICAL, HIGH, MEDIUM, LOW)\n"
        "   - **Script de Remédiation Immédiate** (Fournir un bloc de code Bash, SQL ou Kubectl pour corriger l'incident)\n"
        "   - **Recommandation Long Terme**"
    ),
    output_key="diagnostic_report",
)

quality_checker = LlmAgent(
    name="QualityChecker",
    model=MODEL_NAME,
    tools=[exit_loop],
    description="Vérifie que le rapport contient bien la cause racine et un script de remédiation.",
    instruction=(
        "Examine le rapport dans 'diagnostic_report'.\n"
        "Vérifie qu'il contient la Cause Racine ET un bloc de code de Remédiation.\n"
        "Si TOUT est présent, appelle l'outil `exit_loop` et réponds strictement : OK\n"
        "Sinon, réponds : RETRY"
    ),
)

robust_log_analyzer = LoopAgent(
    name="RobustLogAnalyzer",
    sub_agents=[log_fetcher_agent, quality_checker],
    max_iterations=3,
)

root_agent = robust_log_analyzer