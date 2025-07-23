from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import Client, Facture, CategorieFacture


class FactureModelTest(TestCase):
    """
    Tests pour le modèle Facture.
    
    Teste les fonctionnalités du modèle :
    - Calcul automatique du montant TTC
    - Propriété montant_tva
    - Méthode __str__
    """
    
    def setUp(self):
        """
        Configuration initiale pour chaque test.
        Crée un client et une catégorie nécessaires pour les factures.
        """
        self.client_obj = Client.objects.create(
            nom="Test Client",
            type_client="entreprise",
            email="test@example.com",
            adresse="123 Rue Test",
            code_postal="75001",
            ville="Paris",
            pays="France"
        )
        
        self.categorie = CategorieFacture.objects.create(
            nom="Services",
            description="Prestations de services",
            couleur="#007bff"
        )
    
    def test_calcul_montant_ttc_automatique(self):
        """
        Test du calcul automatique du montant TTC lors de la sauvegarde.
        
        Vérifie que le montant TTC est calculé correctement selon la formule :
        montant_ttc = montant_ht * (1 + taux_tva / 100)
        """
        facture = Facture.objects.create(
            numero="FAC-2025-001",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('100.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='brouillon',
            description="Test de calcul TTC"
        )
        
        # Le montant TTC doit être calculé automatiquement
        self.assertEqual(facture.montant_ttc, Decimal('120.00'))
    
    def test_propriete_montant_tva(self):
        """
        Test de la propriété calculée montant_tva.
        
        Vérifie que la propriété retourne la différence entre TTC et HT.
        """
        facture = Facture.objects.create(
            numero="FAC-2025-002",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('150.00'),
            taux_tva=Decimal('10.00'),
            categorie=self.categorie,
            statut='envoyee',
            description="Test propriété TVA"
        )
        
        # TVA = 150 * 0.10 = 15.00
        self.assertEqual(facture.montant_tva, Decimal('15.00'))
    
    def test_str_representation(self):
        """
        Test de la méthode __str__ du modèle Facture.
        
        Vérifie que la représentation textuelle est au bon format.
        """
        facture = Facture.objects.create(
            numero="FAC-2025-003",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('200.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='payee',
            description="Test représentation textuelle"
        )
        
        expected_str = f"Facture FAC-2025-003 - {self.client_obj.nom}"
        self.assertEqual(str(facture), expected_str)


class FactureListViewTest(TestCase):
    """
    Tests pour la vue de listage des factures (FactureListView).
    
    Teste :
    - Affichage de la liste
    - Filtrage par statut, client, catégorie
    - Recherche textuelle
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests de vue.
        Crée des données de test nécessaires.
        """
        self.test_client = TestClient()
        
        # Création d'objets nécessaires
        self.client_obj = Client.objects.create(
            nom="Client Test Vue",
            type_client="entreprise",
            email="vue@test.com",
            adresse="456 Avenue Test",
            code_postal="75002",
            ville="Paris"
        )
        
        self.categorie = CategorieFacture.objects.create(
            nom="Produits",
            couleur="#28a745"
        )
        
        # Création de plusieurs factures pour tester les filtres
        self.facture1 = Facture.objects.create(
            numero="FAC-LISTE-001",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('100.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='brouillon',
            description="Facture brouillon"
        )
        
        self.facture2 = Facture.objects.create(
            numero="FAC-LISTE-002",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('200.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='envoyee',
            description="Facture envoyée"
        )
        
        self.facture3 = Facture.objects.create(
            numero="FAC-LISTE-003",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('300.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='payee',
            description="Facture payée"
        )
    
    def test_liste_factures_affichage_complet(self):
        """
        Test de l'affichage complet de la liste des factures.
        
        Vérifie que toutes les factures sont affichées sans filtre.
        """
        url = reverse('django_exo_1:facture_list')
        response = self.test_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Liste des Factures")
        self.assertContains(response, "FAC-LISTE-001")
        self.assertContains(response, "FAC-LISTE-002")
        self.assertContains(response, "FAC-LISTE-003")
        self.assertEqual(len(response.context['factures']), 3)
    
    def test_filtrage_par_statut(self):
        """
        Test du filtrage des factures par statut.
        
        Vérifie que le filtre par statut fonctionne correctement.
        """
        url = reverse('django_exo_1:facture_list')
        
        # Test filtre statut "envoyee"
        response = self.test_client.get(url, {'statut': 'envoyee'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['factures']), 1)
        self.assertContains(response, "FAC-LISTE-002")
        self.assertNotContains(response, "FAC-LISTE-001")
        self.assertNotContains(response, "FAC-LISTE-003")
    
    def test_recherche_textuelle(self):
        """
        Test de la recherche textuelle dans les factures.
        
        Vérifie que la recherche fonctionne sur le numéro et le nom du client.
        """
        url = reverse('django_exo_1:facture_list')
        
        # Test recherche par numéro de facture
        response = self.test_client.get(url, {'search': 'LISTE-002'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['factures']), 1)
        self.assertContains(response, "FAC-LISTE-002")
        
        # Test recherche par nom de client
        response = self.test_client.get(url, {'search': 'Client Test Vue'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['factures']), 3)


class FactureDetailViewTest(TestCase):
    """
    Tests pour la vue de détail d'une facture (FactureDetailView).
    
    Teste :
    - Affichage des détails d'une facture
    - Gestion des factures inexistantes
    - Contexte de la vue
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests de vue détail.
        """
        self.test_client = TestClient()
        
        self.client_obj = Client.objects.create(
            nom="Client Détail",
            type_client="particulier",
            email="detail@test.com",
            adresse="789 Boulevard Test",
            code_postal="75003",
            ville="Paris"
        )
        
        self.categorie = CategorieFacture.objects.create(
            nom="Consulting",
            couleur="#ffc107"
        )
        
        self.facture = Facture.objects.create(
            numero="FAC-DETAIL-001",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('500.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='envoyee',
            description="Facture pour test de détail"
        )
    
    def test_affichage_detail_facture_existante(self):
        """
        Test de l'affichage des détails d'une facture existante.
        
        Vérifie que toutes les informations importantes sont affichées.
        """
        url = reverse('django_exo_1:facture_detail', kwargs={'pk': self.facture.pk})
        response = self.test_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FAC-DETAIL-001")
        self.assertContains(response, "Client Détail")
        self.assertContains(response, "500.00")  # Montant HT
        self.assertContains(response, "600.00")  # Montant TTC
        self.assertContains(response, "Consulting")
        self.assertContains(response, "Envoyée")
    
    def test_facture_inexistante_retourne_404(self):
        """
        Test qu'une facture inexistante retourne une erreur 404.
        """
        url = reverse('django_exo_1:facture_detail', kwargs={'pk': 99999})
        response = self.test_client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_contexte_vue_detail(self):
        """
        Test que le contexte de la vue contient les bonnes données.
        """
        url = reverse('django_exo_1:facture_detail', kwargs={'pk': self.facture.pk})
        response = self.test_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['facture'], self.facture)
        self.assertEqual(response.context['facture'].montant_tva, Decimal('100.00'))


class FactureCreateViewTest(TestCase):
    """
    Tests pour la vue de création d'une facture (FactureCreateView).
    
    Teste :
    - Affichage du formulaire de création
    - Création valide d'une facture
    - Validation des erreurs de formulaire
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests de création.
        """
        self.test_client = TestClient()
        
        self.client_obj = Client.objects.create(
            nom="Client Création",
            type_client="entreprise",
            email="creation@test.com",
            adresse="321 Rue Création",
            code_postal="75004",
            ville="Paris"
        )
        
        self.categorie = CategorieFacture.objects.create(
            nom="Formation",
            couleur="#dc3545"
        )
    
    def test_affichage_formulaire_creation(self):
        """
        Test de l'affichage du formulaire de création de facture.
        
        Vérifie que le formulaire s'affiche correctement avec tous les champs.
        """
        url = reverse('django_exo_1:facture_create')
        response = self.test_client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nouvelle Facture")
        self.assertContains(response, 'name="numero"')
        self.assertContains(response, 'name="client"')
        self.assertContains(response, 'name="montant_ht"')
        self.assertContains(response, 'name="categorie"')
    
    def test_creation_facture_valide(self):
        """
        Test de création d'une facture avec des données valides.
        
        Vérifie que la facture est créée et sauvegardée correctement.
        """
        url = reverse('django_exo_1:facture_create')
        data = {
            'numero': 'FAC-CREATE-001',
            'date_emission': date.today().strftime('%Y-%m-%d'),
            'date_echeance': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'client': self.client_obj.pk,
            'montant_ht': '750.00',
            'taux_tva': '20.00',
            'categorie': self.categorie.pk,
            'statut': 'brouillon',
            'description': 'Facture de test créée via formulaire'
        }
        
        response = self.test_client.post(url, data)
        
        # Vérification de la redirection après création
        self.assertEqual(response.status_code, 302)
        
        # Vérification que la facture a été créée
        facture = Facture.objects.get(numero='FAC-CREATE-001')
        self.assertEqual(facture.client, self.client_obj)
        self.assertEqual(facture.montant_ht, Decimal('750.00'))
        self.assertEqual(facture.montant_ttc, Decimal('900.00'))  # 750 + 20% TVA
        self.assertEqual(facture.categorie, self.categorie)
    
    def test_creation_facture_donnees_invalides(self):
        """
        Test de création d'une facture avec des données invalides.
        
        Vérifie que les erreurs de validation sont gérées correctement.
        """
        url = reverse('django_exo_1:facture_create')
        data = {
            'numero': '',  # Numéro manquant (requis)
            'date_emission': '',  # Date manquante (requise)
            'montant_ht': '-100.00',  # Montant négatif (invalide)
            'description': ''  # Description manquante (requise)
        }
        
        response = self.test_client.post(url, data)
        
        # Le formulaire doit rester affiché avec les erreurs
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'numero', 'This field is required.')
        
        # Vérification qu'aucune facture n'a été créée
        self.assertEqual(Facture.objects.count(), 0)


class FactureBulkActionTest(TestCase):
    """
    Tests pour la fonctionnalité d'actions de lot sur les factures.
    
    Teste :
    - Marquage multiple de factures comme payées
    - Gestion des erreurs (aucune sélection, factures déjà payées)
    - Validation des permissions et redirections
    """
    
    def setUp(self):
        """
        Configuration initiale pour les tests d'actions de lot.
        """
        self.test_client = TestClient()
        
        self.client_obj = Client.objects.create(
            nom="Client Bulk Action",
            type_client="entreprise",
            email="bulk@test.com",
            adresse="999 Rue Bulk",
            code_postal="75009",
            ville="Paris"
        )
        
        self.categorie = CategorieFacture.objects.create(
            nom="Actions Lot",
            couleur="#6f42c1"
        )
        
        # Création de plusieurs factures pour tester les actions de lot
        self.facture_brouillon = Facture.objects.create(
            numero="FAC-BULK-001",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('100.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='brouillon',
            description="Facture brouillon pour test bulk"
        )
        
        self.facture_envoyee = Facture.objects.create(
            numero="FAC-BULK-002",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('200.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='envoyee',
            description="Facture envoyée pour test bulk"
        )
        
        self.facture_deja_payee = Facture.objects.create(
            numero="FAC-BULK-003",
            date_emission=date.today(),
            date_echeance=date.today() + timedelta(days=30),
            client=self.client_obj,
            montant_ht=Decimal('300.00'),
            taux_tva=Decimal('20.00'),
            categorie=self.categorie,
            statut='payee',
            description="Facture déjà payée pour test bulk"
        )
    
    def test_marquage_multiple_comme_payees(self):
        """
        Test du marquage de plusieurs factures comme payées en une fois.
        
        Vérifie que les factures sélectionnées sont bien marquées comme payées.
        """
        url = reverse('django_exo_1:facture_bulk_action')
        data = {
            'action': 'mark_paid',
            'selected_factures': [
                str(self.facture_brouillon.pk),
                str(self.facture_envoyee.pk)
            ]
        }
        
        response = self.test_client.post(url, data)
        
        # Vérification de la redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('django_exo_1:facture_list'))
        
        # Vérification que les factures ont été mises à jour
        self.facture_brouillon.refresh_from_db()
        self.facture_envoyee.refresh_from_db()
        self.facture_deja_payee.refresh_from_db()
        
        self.assertEqual(self.facture_brouillon.statut, 'payee')
        self.assertEqual(self.facture_envoyee.statut, 'payee')
        self.assertEqual(self.facture_deja_payee.statut, 'payee')  # Inchangée
    
    def test_aucune_facture_selectionnee(self):
        """
        Test du cas où aucune facture n'est sélectionnée.
        
        Vérifie que l'action échoue avec un message d'erreur approprié.
        """
        url = reverse('django_exo_1:facture_bulk_action')
        data = {
            'action': 'mark_paid',
            'selected_factures': []
        }
        
        response = self.test_client.post(url, data)
        
        # Vérification de la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérification qu'aucune facture n'a été modifiée
        self.facture_brouillon.refresh_from_db()
        self.facture_envoyee.refresh_from_db()
        
        self.assertEqual(self.facture_brouillon.statut, 'brouillon')
        self.assertEqual(self.facture_envoyee.statut, 'envoyee')
    
    def test_factures_deja_payees_ignorees(self):
        """
        Test que les factures déjà payées sont ignorées lors de l'action de lot.
        
        Vérifie que seules les factures non payées sont mises à jour.
        """
        url = reverse('django_exo_1:facture_bulk_action')
        data = {
            'action': 'mark_paid',
            'selected_factures': [
                str(self.facture_deja_payee.pk)  # Déjà payée
            ]
        }
        
        response = self.test_client.post(url, data)
        
        # Vérification de la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérification que la facture reste inchangée
        self.facture_deja_payee.refresh_from_db()
        self.assertEqual(self.facture_deja_payee.statut, 'payee')
