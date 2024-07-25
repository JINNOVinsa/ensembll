# Utiliser une image de base officielle de Python
FROM python:3.9-slim

# Installer les locales
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/*
RUN echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR:fr
ENV LC_ALL fr_FR.UTF-8

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requirements.txt dans le répertoire de travail
COPY requirements.txt requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du projet dans le répertoire de travail
COPY . .

# Exposer le port sur lequel l'application va écouter
EXPOSE 8000

# Définir la commande par défaut pour exécuter l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
