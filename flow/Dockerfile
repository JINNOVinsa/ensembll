# Utiliser une image de base officielle de Python
FROM python:3.9-slim


# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requirements.txt dans le répertoire de travail
COPY requirements.txt requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du projet dans le répertoire de travail
COPY . .

# Exposer le port sur lequel Gunicorn va écouter
EXPOSE 8001

# Définir la commande par défaut pour exécuter l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "app:app"]
