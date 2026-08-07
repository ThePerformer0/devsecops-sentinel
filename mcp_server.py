import json
import sys
import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DevSecOps-LogCollector")

# Base de données dynamique de logs système
MOCK_LOGS = {
    "auth-service": [
        "2026-08-07 00:00:01 [INFO] [auth-service] Healthcheck OK - HTTP 200",
        "2026-08-07 00:05:12 [ERROR] [auth-service] DBConnectionTimeoutException: Unable to acquire connection from pool (max_size=20, active=20) after 5000ms. Host: db-primary.internal",
    ],
    "payment-service": [
        "2026-08-07 00:06:45 [CRITICAL] [payment-service] StripeAPIError: API Key invalid or expired. Failed to process transaction_id=tx_99482.",
    ],
    "frontend-service": [
        "2026-08-07 00:07:01 [WARN] [frontend-service] SlowResponseWarning: TTFB exceeded 3000ms for route /checkout.",
    ]
}

@mcp.tool()
def fetch_filtered_logs(service_name: str, min_severity: str = "ERROR") -> str:
    """Récupère les logs filtrés d'un service par niveau de sévérité.
    
    Args:
        service_name: Nom du microservice (auth-service, payment-service, frontend-service)
        min_severity: Niveau minimum (ERROR ou CRITICAL)
    """
    logs = MOCK_LOGS.get(service_name, [])
    severities = ["ERROR", "CRITICAL"] if min_severity == "ERROR" else ["CRITICAL"]
    
    filtered = [log for log in logs if any(level in log for level in severities)]
    
    if filtered:
        return json.dumps({
            "status": "success", 
            "service": service_name, 
            "logs": filtered
        })
    return json.dumps({
        "status": "no_errors_found", 
        "message": f"Aucun log de sévérité >= {min_severity} trouvé pour {service_name}."
    })

@mcp.tool()
def inject_chaos_incident(service_name: str, incident_type: str) -> str:
    """Simule une injection de panne (Chaos Engineering) sur un service.
    
    Args:
        service_name: Nom du service ciblé.
        incident_type: Type de panne (memory_leak, latency_spike, cert_expired).
    """
    incidents = {
        "memory_leak": "2026-08-07 01:10:00 [CRITICAL] OOMKilled: Process consumed 100% RAM allocation (4GB/4GB). Container terminated.",
        "latency_spike": "2026-08-07 01:10:00 [ERROR] GatewayTimeout: Upstream HTTP response time exceeded 10000ms on endpoint /api/v1/data.",
        "cert_expired": "2026-08-07 01:10:00 [CRITICAL] SSLError: TLS Certificate expired on 2026-08-06. Handshake failed."
    }
    log_entry = incidents.get(incident_type, "2026-08-07 01:10:00 [ERROR] Unknown system failure.")
    
    if service_name not in MOCK_LOGS:
        MOCK_LOGS[service_name] = []
    MOCK_LOGS[service_name].append(log_entry)
    
    return json.dumps({
        "status": "injected", 
        "service": service_name, 
        "injected_log": log_entry
    })

if __name__ == "__main__":
    mcp.run(transport="stdio")