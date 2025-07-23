# Système de Gestion des Factures Django

Une application Django complète pour la gestion des factures avec catégorisation.

## Installation et lancement

### Prérequis

- Python 3.9+
- Django 4.2+

### Étapes d'installation

1. **Activer l'environnement virtuel** (déjà configuré) :

   ```bash
   source env/bin/activate
   ```

2. **Appliquer les migrations** (déjà fait) :

   ```bash
   python manage.py migrate
   ```

3. **Créer des données de test** (déjà fait) :

   ```bash
   python manage.py create_test_data
   ```

4. **Lancer le serveur de développement** :

   ```bash
   python manage.py runserver
   # ou utiliser le script
   ./run.sh
   ```

5. **Accéder à l'application** :
   - Interface principale : http://127.0.0.1:8000/
   - Administration Django : http://127.0.0.1:8000/admin/

## Tests

### Exécuter tous les tests

Pour lancer tous les tests de l'application :

```bash
python manage.py test
```

### Exécuter les tests avec plus de détails

Pour avoir des informations détaillées sur l'exécution des tests :

```bash
python manage.py test --verbosity=2
```
