# Utilise une image de base Python
FROM python:3.9-slim

# Crée un répertoire de travail
WORKDIR /app

# Copie le code et les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose le port du service
EXPOSE 5000

# Lance le serveur Flask
CMD ["python", "app.py"]