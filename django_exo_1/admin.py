"""Configuration de l'interface d'administration Django.

Ce module définit la configuration de l'interface d'administration Django
pour les modèles Client, CategorieFacture et Facture. Il personnalise
l'affichage, les filtres, la recherche et l'organisation des formulaires
pour faciliter la gestion des données par les administrateurs.

Classes:
    ClientAdmin: Configuration d'administration pour les clients
    CategorieFactureAdmin: Configuration d'administration pour les catégories
    FactureAdmin: Configuration d'administration pour les factures

Note:
    Toutes les classes utilisent le décorateur @admin.register pour
    l'enregistrement automatique des modèles dans l'interface d'administration.

Author: Équipe de développement
Date: 2025-07-22
Version: 1.0
"""

from django.contrib import admin
from .models import Client, CategorieFacture, Facture, LogCreationFacture, LogCreationFacture


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les clients.
    
    Personnalise l'affichage et les fonctionnalités de l'admin Django pour
    faciliter la gestion des clients par les administrateurs.
    
    Cette classe configure l'interface d'administration Django pour le modèle Client,
    en définissant l'affichage en liste, les filtres, la recherche et l'organisation
    du formulaire de saisie.
    
    Attributes:
        list_display (tuple): Colonnes affichées dans la liste des clients.
            Contient les champs: nom, type_client, email, ville, est_actif, date_creation.
        list_filter (tuple): Filtres disponibles dans la barre latérale.
            Permet de filtrer par: type_client, est_actif, pays, date_creation.
        search_fields (tuple): Champs recherchables dans la barre de recherche.
            Permet la recherche dans: nom, email, ville, siret.
        ordering (tuple): Ordre de tri par défaut des enregistrements.
            Tri alphabétique par nom du client.
        readonly_fields (tuple): Champs en lecture seule dans le formulaire.
            Champs automatiques: date_creation, date_modification.
        fieldsets (tuple): Organisation des champs en sections dans le formulaire.
            Définit 5 sections: Informations principales, Coordonnées, 
            Informations entreprise, Notes, Métadonnées.
    
    Note:
        Les sections "Informations entreprise" et "Métadonnées" sont repliables
        par défaut pour améliorer l'ergonomie du formulaire.
    
    Example:
        Cette configuration permet aux administrateurs de:
        - Visualiser rapidement les clients essentiels
        - Filtrer par type, statut actif, pays et date
        - Rechercher par nom, email, ville et SIRET
        - Saisir les informations de manière organisée
    """
    # Configuration d'affichage - Définit les colonnes visibles dans la vue liste
    list_display = ('nom', 'type_client', 'email', 'ville', 'est_actif', 'date_creation')
    
    # Configuration de filtrage - Ajoute des filtres dans la barre latérale
    list_filter = ('type_client', 'est_actif', 'pays', 'date_creation')
    
    # Configuration de recherche - Définit les champs recherchables
    search_fields = ('nom', 'email', 'ville', 'siret')
    
    # Configuration de tri - Définit l'ordre par défaut des enregistrements
    ordering = ('nom',)
    
    # Configuration des champs en lecture seule - Protège les champs automatiques
    readonly_fields = ('date_creation', 'date_modification')
    
    # Organisation du formulaire en sections logiques
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'type_client', 'est_actif'),
            'description': 'Informations de base du client'
        }),
        ('Coordonnées', {
            'fields': ('email', 'telephone', 'adresse', 'code_postal', 'ville', 'pays'),
            'description': 'Informations de contact et adresse'
        }),
        ('Informations entreprise', {
            'fields': ('siret', 'numero_tva'),
            'classes': ('collapse',),  # Section repliable
            'description': 'Informations légales pour les entreprises'
        }),
        ('Notes', {
            'fields': ('notes',),
            'description': 'Notes libres sur le client'
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',),  # Section repliable
            'description': 'Informations de suivi automatique'
        }),
    )


@admin.register(CategorieFacture)
class CategorieFactureAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les catégories de factures.
    
    Interface simple pour gérer les catégories avec affichage de la couleur
    et possibilité de recherche et filtrage.
    
    Cette classe configure l'interface d'administration Django pour le modèle
    CategorieFacture, permettant la gestion des catégories utilisées pour
    classifier les factures.
    
    Attributes:
        list_display (tuple): Colonnes affichées dans la liste des catégories.
            Contient les champs: nom, description, couleur, date_creation.
        list_filter (tuple): Filtres disponibles dans la barre latérale.
            Permet de filtrer par: date_creation.
        search_fields (tuple): Champs recherchables dans la barre de recherche.
            Permet la recherche dans: nom, description.
        ordering (tuple): Ordre de tri par défaut des enregistrements.
            Tri alphabétique par nom de la catégorie.
    
    Note:
        L'affichage de la couleur dans la liste facilite l'identification
        visuelle des différentes catégories de factures.
    
    Example:
        Cette configuration permet aux administrateurs de:
        - Visualiser toutes les catégories avec leur couleur
        - Filtrer par date de création
        - Rechercher dans le nom et la description
        - Maintenir un ordre alphabétique
    """
    # Configuration d'affichage - Colonnes visibles avec informations essentielles
    list_display = ('nom', 'description', 'couleur', 'date_creation')
    
    # Configuration de filtrage - Filtre par période de création
    list_filter = ('date_creation',)
    
    # Configuration de recherche - Recherche textuelle dans nom et description
    search_fields = ('nom', 'description')
    
    # Configuration de tri - Ordre alphabétique par nom de catégorie
    ordering = ('nom',)


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les factures.
    
    Interface complète pour gérer les factures avec affichage des informations
    essentielles, filtres avancés et recherche multi-critères.
    
    Cette classe configure l'interface d'administration Django pour le modèle
    Facture, offrant une gestion complète des factures avec des fonctionnalités
    avancées de filtrage, recherche et organisation des données.
    
    Attributes:
        list_display (tuple): Colonnes essentielles affichées dans la liste.
            Contient les champs: numero, client, date_emission, date_echeance,
            montant_ht, montant_ttc, categorie, statut.
        list_filter (tuple): Filtres disponibles dans la barre latérale.
            Permet de filtrer par: statut, categorie, date_emission, 
            date_echeance, client__type_client.
        search_fields (tuple): Champs recherchables dans la barre de recherche.
            Permet la recherche dans: numero, client__nom, client__email.
        ordering (tuple): Ordre de tri par défaut des enregistrements.
            Tri par date d'émission décroissante puis par numéro décroissant.
        readonly_fields (tuple): Champs en lecture seule dans le formulaire.
            Champs protégés: montant_ttc, date_creation, date_modification.
        fieldsets (tuple): Organisation des champs en sections dans le formulaire.
            Définit 6 sections: Informations principales, Client, Montants,
            Catégorie et statut, Description, Métadonnées.
    
    Note:
        Le montant TTC est calculé automatiquement et protégé en lecture seule.
        La section "Métadonnées" est repliable pour améliorer l'ergonomie.
        Les filtres incluent le type de client pour un filtrage avancé.
    
    Example:
        Cette configuration permet aux administrateurs de:
        - Visualiser les factures avec toutes les informations critiques
        - Filtrer par statut, catégorie, dates et type de client
        - Rechercher dans les numéros de facture et informations client
        - Saisir les données de manière structurée et logique
        - Protéger les champs calculés automatiquement
    """
    # Configuration d'affichage - Vue liste complète avec informations critiques
    list_display = ('numero', 'client', 'date_emission', 'date_echeance', 
                    'montant_ht', 'montant_ttc', 'categorie', 'statut')
    
    # Configuration de filtrage - Filtres multiples pour navigation avancée
    list_filter = ('statut', 'categorie', 'date_emission', 'date_echeance', 'client__type_client')
    
    # Configuration de recherche - Recherche dans factures et clients associés
    search_fields = ('numero', 'client__nom', 'client__email')
    
    # Configuration de tri - Tri chronologique décroissant prioritaire
    ordering = ('-date_emission', '-numero')
    
    # Configuration des champs protégés - Champs calculés et métadonnées
    readonly_fields = ('montant_ttc', 'date_creation', 'date_modification')
    
    # Organisation du formulaire de facture en sections logiques
    fieldsets = (
        ('Informations principales', {
            'fields': ('numero', 'date_emission', 'date_echeance'),
            'description': 'Informations de base de la facture'
        }),
        ('Client', {
            'fields': ('client',),
            'description': 'Client associé à cette facture'
        }),
        ('Montants', {
            'fields': ('montant_ht', 'taux_tva', 'montant_ttc'),
            'description': 'Montants et calculs de TVA (TTC calculé automatiquement)'
        }),
        ('Catégorie et statut', {
            'fields': ('categorie', 'statut'),
            'description': 'Classification et état de la facture'
        }),
        ('Description', {
            'fields': ('description', 'notes'),
            'description': 'Contenu et notes de la facture'
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',),  # Section repliable
            'description': 'Informations de suivi automatique'
        }),
    )


@admin.register(LogCreationFacture)
class LogCreationFactureAdmin(admin.ModelAdmin):
    """Configuration de l'interface d'administration pour les logs de création de factures.
    
    Interface d'administration en lecture seule pour consulter l'historique
    des créations de factures enregistrées par le middleware.
    
    Cette classe configure l'affichage des logs de création de factures,
    permettant aux administrateurs de suivre quand et comment les factures
    ont été créées, avec toutes les métadonnées associées.
    
    Attributes:
        list_display (tuple): Colonnes affichées dans la liste des logs.
        list_filter (tuple): Filtres disponibles dans la barre latérale.
        search_fields (tuple): Champs recherchables.
        readonly_fields (tuple): Tous les champs en lecture seule.
        ordering (tuple): Ordre de tri par défaut (plus récent d'abord).
        fieldsets (tuple): Organisation des champs dans le formulaire de détail.
    """
    
    list_display = (
        'facture',
        'date_creation',
        'ip_address',
        'methode_http',
        'get_numero_facture',
        'get_client_facture'
    )
    
    list_filter = (
        'date_creation',
        'methode_http',
        'facture__statut',
        'facture__categorie',
    )
    
    search_fields = (
        'facture__numero',
        'facture__client__nom',
        'ip_address',
        'user_agent',
    )
    
    # Tous les champs en lecture seule car c'est un log
    readonly_fields = (
        'facture',
        'user_agent',
        'ip_address',
        'referer',
        'date_creation',
        'session_key',
        'methode_http',
        'donnees_post',
        'get_donnees_sanitisees',
    )
    
    ordering = ('-date_creation',)
    
    # Désactiver les actions de modification/suppression
    def has_add_permission(self, request):
        """Désactive l'ajout manuel de logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Autorise uniquement la lecture des logs."""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Désactive la suppression de logs."""
        return False
    
    # Méthodes personnalisées pour l'affichage
    def get_numero_facture(self, obj):
        """Retourne le numéro de la facture associée."""
        return obj.facture.numero
    get_numero_facture.short_description = 'Numéro facture'
    get_numero_facture.admin_order_field = 'facture__numero'
    
    def get_client_facture(self, obj):
        """Retourne le nom du client de la facture."""
        return obj.facture.client.nom
    get_client_facture.short_description = 'Client'
    get_client_facture.admin_order_field = 'facture__client__nom'
    
    def get_donnees_sanitisees(self, obj):
        """Affiche les données POST sanitisées."""
        import json
        if obj.donnees_sanitisees:
            return json.dumps(obj.donnees_sanitisees, indent=2)
        return "Aucune donnée"
    get_donnees_sanitisees.short_description = 'Données POST (sanitisées)'
    
    fieldsets = (
        ('Facture associée', {
            'fields': ('facture',),
            'description': 'Facture qui a été créée'
        }),
        ('Informations de la requête', {
            'fields': ('date_creation', 'methode_http', 'ip_address', 'referer'),
            'description': 'Métadonnées de la requête HTTP'
        }),
        ('Informations techniques', {
            'fields': ('user_agent', 'session_key'),
            'classes': ('collapse',),
            'description': 'Détails techniques de la session'
        }),
        ('Données du formulaire', {
            'fields': ('get_donnees_sanitisees', 'donnees_post'),
            'classes': ('collapse',),
            'description': 'Données soumises lors de la création'
        }),
    )
