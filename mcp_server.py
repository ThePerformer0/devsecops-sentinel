import json
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DevSecOps-LogCollector")

# Simulation d'un fichier de logs dense (bruit + erreurs)
RAW_LOG_FILE = [
    "2026-08-07 00:00:01 [INFO] [auth-service] Healthcheck OK - HTTP 200",
    "2026-08-07 00:01:15 [INFO] [auth-service] User session refreshed id=8841",
    "2026-08-07 00:03:22 [INFO] [auth-service] Healthcheck OK - HTTP 200",
    "2026-08-07 00:05:12 [ERROR] [auth-service] DBConnectionTimeoutException: Unable to acquire connection from pool (max_size=20, active=20) after 5000ms. Host: db-primary.internal",
    "2026-08-07 00:05:13 [INFO] [auth-service] Retry connection attempt 1/3...",
    "2026-08-07 00:06:45 [CRITICAL] [payment-service] StripeAPIError: API Key invalid or expired. Failed to process transaction_id=tx_99482.",
    "2026-08-07 00:07:01 [WARN] [frontend-service] SlowResponseWarning: TTFB exceeded 3000ms for route /checkout.",
    "2026-08-07 00:08:00 [INFO] [auth-service] Healthcheck OK - HTTP 200",
]

@mcp.tool()
def fetch_filtered_logs(service_name: str, min_severity: str = "ERROR") -> str:
    """Récupère uniquement les logs filtrés par sévérité pour éviter de polluer le contexte de l'agent.
    
    Args:
        service_name: Nom du service (auth-service, payment-service, frontend-service)
        min_severity: Niveau minimum de sévérité à extraire (ERROR ou CRITICAL)
    """
    severities = ["ERROR", "CRITICAL"] if min_severity == "ERROR" else ["CRITICAL"]
    
    # Context Engineering: On sélectionne uniquement les lignes pertinentes
    filtered = [
        log for log in RAW_LOG_FILE 
        if service_name in log and any(level in log for level in severities)
    ]
    
    if filtered:
        return json.dumps({
            "status": "success", 
            "service": service_name, 
            "total_lines_analyzed": len(RAW_LOG_FILE),
            "relevant_logs_count": len(filtered),
            "logs": filtered
        })
    else:
        return json.dumps({
            "status": "no_errors_found", 
            "message": f"Aucun log de sévérité >= {min_severity} trouvé pour {service_name}."
        })

if __name__ == "__main__":
    mcp.run(transport="stdio")