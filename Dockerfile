# Dockerfile

# Même version que ton venv local
FROM python:3.13-slim

# Répertoire de travail
WORKDIR /app

# Dépendances système minimales (pour compiler certains paquets)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Installer les libs Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet dans l'image
COPY . .

# Pour Meltano/dbt
ENV MELTANO_PROJECT_ROOT=/app

# Commande par défaut (surchargée par docker-compose)
CMD ["bash"]
