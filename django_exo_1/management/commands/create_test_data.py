from django.core.management.base import BaseCommand
from django_exo_1.models import Client, CategorieFacture, Facture
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Crée des données de test pour l\'application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la création des factures même si elles existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de test...'))
        
        # Suppression de toutes les données existantes
        self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
        
        # Supprimer dans l'ordre pour respecter les contraintes de clés étrangères
        factures_count = Facture.objects.count()
        clients_count = Client.objects.count()
        categories_count = CategorieFacture.objects.count()
        
        Facture.objects.all().delete()
        self.stdout.write(f'- {factures_count} factures supprimées')
        
        Client.objects.all().delete()
        self.stdout.write(f'- {clients_count} clients supprimés')
        
        CategorieFacture.objects.all().delete()
        self.stdout.write(f'- {categories_count} catégories supprimées')
        
        self.stdout.write(self.style.SUCCESS('Toutes les données ont été supprimées.'))
        
        # Créer des catégories
        self.stdout.write(self.style.SUCCESS('Création des catégories...'))
        categories = [
            {
                'nom': 'Services',
                'description': 'Prestations de services',
                'couleur': '#007bff'
            },
            {
                'nom': 'Produits',
                'description': 'Vente de produits',
                'couleur': '#28a745'
            },
            {
                'nom': 'Consulting',
                'description': 'Missions de conseil',
                'couleur': '#ffc107'
            },
            {
                'nom': 'Formation',
                'description': 'Sessions de formation',
                'couleur': '#dc3545'
            },
        ]
        
        for cat_data in categories:
            categorie, created = CategorieFacture.objects.get_or_create(
                nom=cat_data['nom'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Catégorie créée: {categorie.nom}')
            else:
                self.stdout.write(f'Catégorie existante: {categorie.nom}')
        
        # Créer des clients de test
        self.stdout.write(self.style.SUCCESS('Création des clients...'))
        clients_test = [
            {
                'nom': 'Entreprise ABC',
                'type_client': 'entreprise',
                'email': 'contact@abc.com',
                'telephone': '01 23 45 67 89',
                'adresse': '123 Rue de la République',
                'code_postal': '75001',
                'ville': 'Paris',
                'pays': 'France',
                'siret': '12345678901234',
                'numero_tva': 'FR12345678901',
            },
            {
                'nom': 'Société XYZ',
                'type_client': 'entreprise',
                'email': 'admin@xyz.fr',
                'telephone': '04 56 78 90 12',
                'adresse': '456 Avenue des Champs',
                'code_postal': '69000',
                'ville': 'Lyon',
                'pays': 'France',
                'siret': '98765432109876',
                'numero_tva': 'FR98765432109',
            },
            {
                'nom': 'Start-up Innovation',
                'type_client': 'entreprise',
                'email': 'ceo@innovation.com',
                'telephone': '05 12 34 56 78',
                'adresse': '789 Boulevard Tech',
                'code_postal': '31000',
                'ville': 'Toulouse',
                'pays': 'France',
                'siret': '11111111111111',
                'numero_tva': 'FR11111111111',
            },
            {
                'nom': 'Cabinet Médical Santé+',
                'type_client': 'professionnel',
                'email': 'contact@santeplus.fr',
                'telephone': '04 91 23 45 67',
                'adresse': '12 Place de la Santé',
                'code_postal': '13000',
                'ville': 'Marseille',
                'pays': 'France',
                'siret': '22222222222222',
                'numero_tva': 'FR22222222222',
            },
            {
                'nom': 'Restaurant Le Bistrot',
                'type_client': 'entreprise',
                'email': 'manager@lebistrot.com',
                'telephone': '05 56 78 90 12',
                'adresse': '34 Rue Gastronomique',
                'code_postal': '33000',
                'ville': 'Bordeaux',
                'pays': 'France',
                'siret': '33333333333333',
                'numero_tva': 'FR33333333333',
            },
            {
                'nom': 'École Primaire Saint-Michel',
                'type_client': 'association',
                'email': 'direction@ecole-stmichel.fr',
                'telephone': '02 40 12 34 56',
                'adresse': '56 Avenue de l\'Éducation',
                'code_postal': '44000',
                'ville': 'Nantes',
                'pays': 'France',
                'siret': '44444444444444',
                'numero_tva': 'FR44444444444',
            },
            {
                'nom': 'Garage Auto Réparation',
                'type_client': 'entreprise',
                'email': 'contact@garage-auto.fr',
                'telephone': '03 88 23 45 67',
                'adresse': '78 Route Nationale',
                'code_postal': '67000',
                'ville': 'Strasbourg',
                'pays': 'France',
                'siret': '55555555555555',
                'numero_tva': 'FR55555555555',
            },
            {
                'nom': 'Librairie Papeterie Central',
                'type_client': 'entreprise',
                'email': 'gestion@librairie-central.com',
                'telephone': '02 99 34 56 78',
                'adresse': '90 Rue des Livres',
                'code_postal': '35000',
                'ville': 'Rennes',
                'pays': 'France',
                'siret': '66666666666666',
                'numero_tva': 'FR66666666666',
            },
            {
                'nom': 'Pharmacie de la Place',
                'type_client': 'professionnel',
                'email': 'contact@pharmacie-place.fr',
                'telephone': '03 80 45 67 89',
                'adresse': '23 Place du Marché',
                'code_postal': '21000',
                'ville': 'Dijon',
                'pays': 'France',
                'siret': '77777777777777',
                'numero_tva': 'FR77777777777',
            },
            {
                'nom': 'Association Sport & Loisirs',
                'type_client': 'association',
                'email': 'president@sport-loisirs.org',
                'telephone': '02 35 56 78 90',
                'adresse': '45 Chemin du Stade',
                'code_postal': '76000',
                'ville': 'Rouen',
                'pays': 'France',
                'siret': '88888888888888',
                'numero_tva': 'FR88888888888',
            },
            {
                'nom': 'Cabinet d\'Architectes Moderne',
                'type_client': 'professionnel',
                'email': 'contact@archi-moderne.fr',
                'telephone': '04 93 67 89 01',
                'adresse': '67 Boulevard des Créateurs',
                'code_postal': '06000',
                'ville': 'Nice',
                'pays': 'France',
                'siret': '99999999999999',
                'numero_tva': 'FR99999999999',
            },
            {
                'nom': 'Boulangerie Artisanale Dupont',
                'type_client': 'entreprise',
                'email': 'contact@boulangerie-dupont.fr',
                'telephone': '03 83 78 90 12',
                'adresse': '89 Rue du Pain',
                'code_postal': '54000',
                'ville': 'Nancy',
                'pays': 'France',
                'siret': '10101010101010',
                'numero_tva': 'FR10101010101',
            },
        ]
        
        created_clients = []
        for client_data in clients_test:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults=client_data
            )
            created_clients.append(client)
            if created:
                self.stdout.write(f'Client créé: {client.nom}')
            else:
                self.stdout.write(f'Client existant: {client.nom}')
        
        # Créer des factures de test
        self.stdout.write(self.style.SUCCESS('Création des factures...'))
        categories_obj = list(CategorieFacture.objects.all())
        
        factures_test = [
                {
                    'numero': 'FACT-2024-001',
                    'client': created_clients[0],  # Entreprise ABC
                    'montant_ht': Decimal('1500.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[0],
                    'statut': 'payee',
                    'description': 'Développement site web',
                    'date_emission': date.today() - timedelta(days=30),
                    'date_echeance': date.today() - timedelta(days=1),
                },
                {
                    'numero': 'FACT-2024-002',
                    'client': created_clients[1],  # Société XYZ
                    'montant_ht': Decimal('2800.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[1],
                    'statut': 'envoyee',
                    'description': 'Vente matériel informatique',
                    'date_emission': date.today() - timedelta(days=15),
                    'date_echeance': date.today() + timedelta(days=15),
                },
                {
                    'numero': 'FACT-2024-003',
                    'client': created_clients[2],  # Start-up Innovation
                    'montant_ht': Decimal('5200.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[2],
                    'statut': 'brouillon',
                    'description': 'Mission de conseil en transformation digitale',
                    'date_emission': date.today(),
                    'date_echeance': date.today() + timedelta(days=30),
                    'notes': 'Mission de 3 mois',
                },
                {
                    'numero': 'FACT-2024-004',
                    'client': created_clients[3],  # Cabinet Médical Santé+
                    'montant_ht': Decimal('980.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[3],
                    'statut': 'payee',
                    'description': 'Formation logiciel de gestion',
                    'date_emission': date.today() - timedelta(days=45),
                    'date_echeance': date.today() - timedelta(days=15),
                },
                {
                    'numero': 'FACT-2024-005',
                    'client': created_clients[4],  # Restaurant Le Bistrot
                    'montant_ht': Decimal('3200.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[1],
                    'statut': 'envoyee',
                    'description': 'Équipement cuisine professionnelle',
                    'date_emission': date.today() - timedelta(days=10),
                    'date_echeance': date.today() + timedelta(days=20),
                },
                {
                    'numero': 'FACT-2024-006',
                    'client': created_clients[5],  # École Primaire Saint-Michel
                    'montant_ht': Decimal('1850.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[3],
                    'statut': 'brouillon',
                    'description': 'Formation numérique pour enseignants',
                    'date_emission': date.today() - timedelta(days=5),
                    'date_echeance': date.today() + timedelta(days=25),
                    'notes': 'Formation en 2 sessions',
                },
                {
                    'numero': 'FACT-2024-007',
                    'client': created_clients[6],  # Garage Auto Réparation
                    'montant_ht': Decimal('4500.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[0],
                    'statut': 'payee',
                    'description': 'Maintenance système informatique',
                    'date_emission': date.today() - timedelta(days=60),
                    'date_echeance': date.today() - timedelta(days=30),
                },
                {
                    'numero': 'FACT-2024-008',
                    'client': created_clients[7],  # Librairie Papeterie Central
                    'montant_ht': Decimal('750.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[2],
                    'statut': 'envoyee',
                    'description': 'Conseil stratégie commerciale',
                    'date_emission': date.today() - timedelta(days=8),
                    'date_echeance': date.today() + timedelta(days=22),
                },
                {
                    'numero': 'FACT-2024-009',
                    'client': created_clients[8],  # Pharmacie de la Place
                    'montant_ht': Decimal('1200.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[1],
                    'statut': 'annulee',
                    'description': 'Mobilier officine',
                    'date_emission': date.today() - timedelta(days=20),
                    'date_echeance': date.today() + timedelta(days=10),
                    'notes': 'Commande annulée par le client',
                },
                {
                    'numero': 'FACT-2024-010',
                    'client': created_clients[9],  # Association Sport & Loisirs
                    'montant_ht': Decimal('680.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[3],
                    'statut': 'brouillon',
                    'description': 'Formation premiers secours',
                    'date_emission': date.today() - timedelta(days=2),
                    'date_echeance': date.today() + timedelta(days=28),
                },
                {
                    'numero': 'FACT-2024-011',
                    'client': created_clients[10],  # Cabinet d'Architectes Moderne
                    'montant_ht': Decimal('8500.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[2],
                    'statut': 'envoyee',
                    'description': 'Audit énergétique et conseil BIM',
                    'date_emission': date.today() - timedelta(days=12),
                    'date_echeance': date.today() + timedelta(days=18),
                    'notes': 'Mission complexe sur 6 mois',
                },
                {
                    'numero': 'FACT-2024-012',
                    'client': created_clients[11],  # Boulangerie Artisanale Dupont
                    'montant_ht': Decimal('2400.00'),
                    'taux_tva': Decimal('20.00'),
                    'categorie': categories_obj[1],
                    'statut': 'payee',
                    'description': 'Four professionnel et équipements',
                    'date_emission': date.today() - timedelta(days=40),
                    'date_echeance': date.today() - timedelta(days=10),
                },
            ]
        
        for facture_data in factures_test:
            facture, created = Facture.objects.get_or_create(
                numero=facture_data['numero'],
                defaults=facture_data
            )
            if created:
                self.stdout.write(f'Facture créée: {facture.numero}')
            else:
                self.stdout.write(f'Facture existante: {facture.numero}')
        
        self.stdout.write(
            self.style.SUCCESS('Données de test créées avec succès!')
        )
