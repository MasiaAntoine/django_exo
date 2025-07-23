from django.core.management.base import BaseCommand
from django_exo_1.models import Client, Facture
from django.db import transaction


class Command(BaseCommand):
    help = 'Migre les données client des factures vers le modèle Client'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule la migration sans effectuer les changements',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode simulation - aucune modification ne sera effectuée'))
        
        self.stdout.write(self.style.SUCCESS('Migration des données client...'))
        
        # Récupérer toutes les factures qui n'ont pas de client assigné
        factures_sans_client = Facture.objects.filter(client__isnull=True)
        
        if not factures_sans_client.exists():
            self.stdout.write(self.style.SUCCESS('Aucune facture sans client trouvée. Migration déjà effectuée.'))
            return
        
        clients_crees = 0
        factures_mises_a_jour = 0
        
        with transaction.atomic():
            # Grouper les factures par nom de client pour éviter les doublons
            clients_data = {}
            
            for facture in factures_sans_client:
                if facture.nom_client not in clients_data:
                    clients_data[facture.nom_client] = {
                        'nom': facture.nom_client,
                        'email': facture.email_client,
                        'adresse_brute': facture.adresse_client,
                        'factures': []
                    }
                clients_data[facture.nom_client]['factures'].append(facture)
            
            for nom_client, data in clients_data.items():
                # Analyser l'adresse pour extraire code postal et ville
                adresse_lignes = data['adresse_brute'].split('\n')
                adresse = adresse_lignes[0] if len(adresse_lignes) > 0 else ''
                
                # Tentative d'extraction du code postal et ville depuis la dernière ligne
                code_postal = ''
                ville = ''
                if len(adresse_lignes) > 1:
                    derniere_ligne = adresse_lignes[-1].strip()
                    # Format attendu: "Code_postal Ville" (ex: "75001 Paris")
                    parties = derniere_ligne.split(' ', 1)
                    if len(parties) >= 2 and parties[0].isdigit():
                        code_postal = parties[0]
                        ville = parties[1]
                    else:
                        ville = derniere_ligne
                
                if not code_postal:
                    code_postal = '00000'  # Code postal par défaut
                if not ville:
                    ville = 'Ville non définie'
                
                # Déterminer le type de client basé sur le nom
                type_client = 'entreprise'  # Par défaut
                nom_lower = nom_client.lower()
                if any(word in nom_lower for word in ['association', 'club', 'syndicat']):
                    type_client = 'association'
                elif any(word in nom_lower for word in ['école', 'collège', 'lycée', 'université', 'mairie', 'préfecture']):
                    type_client = 'administration'
                elif any(word in nom_lower for word in ['monsieur', 'madame', 'mr', 'mme', 'm.']):
                    type_client = 'particulier'
                
                if not dry_run:
                    # Créer ou récupérer le client
                    client, created = Client.objects.get_or_create(
                        nom=data['nom'],
                        email=data['email'],
                        defaults={
                            'type_client': type_client,
                            'adresse': adresse,
                            'code_postal': code_postal,
                            'ville': ville,
                            'telephone': '',
                            'notes': f'Client migré automatiquement depuis les factures existantes'
                        }
                    )
                    
                    if created:
                        clients_crees += 1
                        self.stdout.write(f'Client créé: {client.nom}')
                    
                    # Associer les factures au client
                    for facture in data['factures']:
                        facture.client = client
                        facture.save()
                        factures_mises_a_jour += 1
                        self.stdout.write(f'  Facture {facture.numero} associée au client')
                else:
                    self.stdout.write(f'[SIMULATION] Création du client: {data["nom"]} ({type_client})')
                    self.stdout.write(f'  Adresse: {adresse}')
                    self.stdout.write(f'  Code postal: {code_postal}, Ville: {ville}')
                    self.stdout.write(f'  Email: {data["email"]}')
                    self.stdout.write(f'  Factures à associer: {len(data["factures"])}')
                    clients_crees += 1
                    factures_mises_a_jour += len(data['factures'])
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'SIMULATION - {clients_crees} clients auraient été créés, '
                    f'{factures_mises_a_jour} factures auraient été mises à jour'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migration terminée: {clients_crees} clients créés, '
                    f'{factures_mises_a_jour} factures mises à jour'
                )
            )
