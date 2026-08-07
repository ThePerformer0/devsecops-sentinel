# Image Python officielle ultra-légère
FROM python:3.11-slim

# Repertoire de travail dans le conteneur
WORKDIR /app

# Variable d'environnement pour eviter la mise en cache des sorties stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copie des fichiers de dependances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source complet du projet
COPY . .

# Port expose par defaut par Google Cloud Run
EXPOSE 8080

# Commande mise à jour pour supporter les sessions et autoriser l'hôte
CMD ["adk", "web", "app", "--host", "0.0.0.0", "--port", "8080", "--allow_origins", "*"]