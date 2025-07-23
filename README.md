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

### Tests disponibles

L'application contient des tests complets pour :

- **Modèle Facture** (3 tests) :
  - Calcul automatique du montant TTC
  - Propriété montant_tva
  - Représentation textuelle (__str__)

- **Vue de listage des factures** (3 tests) :
  - Affichage complet de la liste
  - Filtrage par statut
  - Recherche textuelle

- **Vue de détail d'une facture** (3 tests) :
  - Affichage des détails d'une facture existante
  - Gestion des factures inexistantes (404)
  - Validation du contexte de la vue

- **Vue de création d'une facture** (3 tests) :
  - Affichage du formulaire de création
  - Création valide d'une facture
  - Validation des erreurs de formulaire

- **Actions de lot sur les factures** (3 tests) :
  - Marquage multiple de factures comme payées
  - Gestion des erreurs (aucune sélection)
  - Exclusion des factures déjà payées

**Total : 15 tests couvrant les fonctionnalités principales**

### Exemple de sortie des tests

```bash
$ python manage.py test
Found 15 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............
----------------------------------------------------------------------
Ran 15 tests in 0.123s

OK
Destroying test database for alias 'default'...
```
