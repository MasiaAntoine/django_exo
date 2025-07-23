#!/bin/bash

# Chemin vers l'env virtuel
ENV_DIR="./env"

# Active l'environnement virtuel
if [ -d "$ENV_DIR" ]; then
    source "$ENV_DIR/bin/activate"
    echo "✅ Environnement virtuel activé"
else
    echo "❌ Environnement virtuel introuvable : $ENV_DIR"
    exit 1
fi

# Lancer le serveur Django
echo "🚀 Démarrage du serveur Django..."
python manage.py runserver
