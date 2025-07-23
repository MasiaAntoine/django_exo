from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from .models import Client, Facture, CategorieFacture, LogCreationFacture
from .forms import ClientForm, FactureForm, CategorieFactureForm
from .forms import ClientForm, FactureForm, CategorieFactureForm

# Vues de l'application de gestion de factures


def home(request):
    """
    Vue d'accueil avec tableau de bord et statistiques.
    
    Affiche un dashboard avec les principales métriques de l'application :
    - Nombre total de factures et clients
    - Nombre de factures payées et en attente
    - Chiffre d'affaires total (factures payées)
    
    Args:
        request (HttpRequest): Requête HTTP
        
    Returns:
        HttpResponse: Page d'accueil avec les statistiques dans le contexte
        
    Template utilisé:
        django_exo_1/home.html
    """
    # Calcul des statistiques principales avec le manager personnalisé
    stats = Facture.objects.statistiques()
    total_clients = Client.objects.count()
    
    context = {
        'total_factures': stats['total'],
        'total_clients': total_clients,
        'factures_payees': stats['payees'],
        'factures_en_attente': stats['en_attente'],
        'ca_total': stats['chiffre_affaires'],
    }
    return render(request, 'django_exo_1/home.html', context)


# ==========================================
# VUES POUR LA GESTION DES FACTURES
# ==========================================

class FactureCreateView(CreateView):
    """
    Vue basée sur classe pour créer une nouvelle facture.
    
    Utilise un formulaire personnalisé avec validation automatique de la catégorie.
    Si aucune catégorie n'est sélectionnée, le formulaire assigne automatiquement
    la catégorie "Autres".
    
    Attributs:
        model: Modèle Facture
        form_class: FactureForm avec validations personnalisées
        template_name: Template de création
        success_url: Redirection vers la liste après création
        
    Fonctionnalités:
        - Création de facture avec validation complète
        - Messages de succès/erreur à l'utilisateur
        - Gestion automatique de la catégorie par défaut
        - Calcul automatique du montant TTC
    """
    model = Facture
    form_class = FactureForm
    template_name = 'django_exo_1/facture_create.html'
    success_url = reverse_lazy('django_exo_1:facture_list')
    
    def form_valid(self, form):
        """
        Traitement lors de la validation réussie du formulaire.
        
        Args:
            form: Formulaire validé avec les données de la facture
            
        Returns:
            HttpResponse: Redirection vers la page de succès avec message
        """
        # La catégorie est gérée automatiquement dans le clean_categorie du formulaire
        messages.success(self.request, 'La facture a été créée avec succès!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Traitement lors de l'échec de validation du formulaire.
        
        Args:
            form: Formulaire avec erreurs de validation
            
        Returns:
            HttpResponse: Retour au formulaire avec message d'erreur
        """
        messages.error(self.request, 'Erreur lors de la création de la facture. Veuillez vérifier les informations saisies.')
        return super().form_invalid(form)


class FactureListView(ListView):
    """
    Vue basée sur classe pour lister et filtrer les factures.
    
    Affiche une liste paginée des factures avec plusieurs options de filtrage
    et de recherche. Utilise select_related pour optimiser les requêtes.
    
    Attributs:
        model: Modèle Facture
        template_name: Template de liste
        context_object_name: Nom de la variable dans le template
        paginate_by: Nombre d'éléments par page
        
    Fonctionnalités de filtrage:
        - Par statut (brouillon, envoyée, payée, annulée)
        - Par catégorie
        - Par client
        - Recherche textuelle (numéro, nom client, email client)
        
    Optimisations:
        - select_related pour éviter les requêtes N+1
        - Pagination automatique
        - Filtres préservés lors de la navigation
    """
    model = Facture
    template_name = 'django_exo_1/facture_list.html'
    context_object_name = 'factures'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Construction du queryset avec filtres et optimisations.
        
        Applique les filtres basés sur les paramètres GET de l'URL et optimise
        les requêtes avec select_related pour charger les relations en une fois.
        
        Returns:
            QuerySet: Factures filtrées et optimisées
        """
        # Commencer avec le queryset optimisé
        queryset = Facture.objects.avec_relations()
        
        # Filtrage par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtrage par catégorie
        categorie = self.request.GET.get('categorie')
        if categorie:
            queryset = queryset.par_categorie(categorie)
        
        # Filtrage par client
        client = self.request.GET.get('client')
        if client:
            queryset = queryset.par_client(client)
        
        # Recherche textuelle
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.recherche(search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Ajout de données supplémentaires au contexte du template.
        
        Fournit les listes de choix pour les filtres (catégories, clients, statuts).
        
        Args:
            **kwargs: Arguments du contexte parent
            
        Returns:
            dict: Contexte enrichi avec les données de filtrage
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieFacture.objects.all()
        context['clients'] = Client.objects.filter(est_actif=True).order_by('nom')
        context['statuts'] = Facture.STATUT_CHOICES
        return context


class FactureDetailView(DetailView):
    """
    Vue basée sur classe pour afficher le détail d'une facture.
    
    Affiche toutes les informations d'une facture spécifique incluant
    les détails du client, les montants calculés et les métadonnées.
    
    Attributs:
        model: Modèle Facture
        template_name: Template de détail
        context_object_name: Nom de la variable dans le template ('facture')
        
    Fonctionnalités:
        - Affichage complet des informations de la facture
        - Informations client intégrées
        - Montants détaillés (HT, TVA, TTC)
        - Actions d'édition et suppression
    """
    model = Facture
    template_name = 'django_exo_1/facture_detail.html'
    context_object_name = 'facture'


class FactureUpdateView(UpdateView):
    """
    Vue basée sur classe pour modifier une facture existante.
    
    Permet la modification de tous les champs d'une facture avec
    les mêmes validations que lors de la création.
    
    Attributs:
        model: Modèle Facture
        form_class: FactureForm avec validations
        template_name: Template de modification
        
    Fonctionnalités:
        - Modification complète des données de facture
        - Validation identique à la création
        - Recalcul automatique du montant TTC
        - Redirection vers la page de détail après modification
    """
    model = Facture
    form_class = FactureForm
    template_name = 'django_exo_1/facture_update.html'
    
    def get_success_url(self):
        """
        URL de redirection après modification réussie.
        
        Returns:
            str: URL de la page de détail de la facture modifiée
        """
        return reverse_lazy('django_exo_1:facture_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """
        Traitement lors de la validation réussie du formulaire.
        
        Args:
            form: Formulaire validé avec les nouvelles données
            
        Returns:
            HttpResponse: Redirection vers la page de détail avec message
        """
        # La catégorie est gérée automatiquement dans le clean_categorie du formulaire
        messages.success(self.request, 'La facture a été modifiée avec succès!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Traitement lors de l'échec de validation du formulaire.
        
        Args:
            form: Formulaire avec erreurs de validation
            
        Returns:
            HttpResponse: Retour au formulaire avec message d'erreur
        """
        messages.error(self.request, 'Erreur lors de la modification de la facture. Veuillez vérifier les informations saisies.')
        return super().form_invalid(form)


class FactureDeleteView(DeleteView):
    """
    Vue basée sur classe pour supprimer une facture.
    
    Affiche une page de confirmation avant suppression définitive.
    Attention : la suppression est irréversible.
    
    Attributs:
        model: Modèle Facture
        template_name: Template de confirmation de suppression
        success_url: Redirection vers la liste après suppression
        
    Sécurité:
        - Page de confirmation obligatoire
        - Message de succès après suppression
        - Redirection automatique vers la liste
    """
    model = Facture
    template_name = 'django_exo_1/facture_confirm_delete.html'
    success_url = reverse_lazy('django_exo_1:facture_list')
    
    def delete(self, request, *args, **kwargs):
        """
        Traitement de la suppression avec message de confirmation.
        
        Args:
            request: Requête HTTP de suppression
            *args: Arguments positionnels
            **kwargs: Arguments nommés (incluant pk)
            
        Returns:
            HttpResponse: Redirection vers la liste avec message de succès
        """
        messages.success(request, 'La facture a été supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# VUES POUR LA GESTION DES CLIENTS
# ==========================================

class ClientCreateView(CreateView):
    """
    Vue basée sur classe pour créer un nouveau client.
    
    Formulaire complet de création de client avec toutes les informations
    nécessaires pour la facturation (contact, adresse, informations légales).
    
    Attributs:
        model: Modèle Client
        form_class: ClientForm avec widgets Bootstrap
        template_name: Template de création
        success_url: Redirection vers la liste des clients
        
    Fonctionnalités:
        - Création complète des informations client
        - Validation des champs obligatoires
        - Support des entreprises avec SIRET/TVA
        - Gestion des différents types de clients
    """
    model = Client
    form_class = ClientForm
    template_name = 'django_exo_1/client_create.html'
    success_url = reverse_lazy('django_exo_1:client_list')
    
    def form_valid(self, form):
        """
        Traitement lors de la validation réussie du formulaire.
        
        Args:
            form: Formulaire validé avec les données du client
            
        Returns:
            HttpResponse: Redirection vers la liste avec message de succès
        """
        messages.success(self.request, 'Le client a été créé avec succès!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Traitement lors de l'échec de validation du formulaire.
        
        Args:
            form: Formulaire avec erreurs de validation
            
        Returns:
            HttpResponse: Retour au formulaire avec message d'erreur
        """
        messages.error(self.request, 'Erreur lors de la création du client. Veuillez vérifier les informations saisies.')
        return super().form_invalid(form)


class ClientListView(ListView):
    """
    Vue basée sur classe pour lister et filtrer les clients.
    
    Affiche une liste paginée des clients avec options de filtrage
    et de recherche. Utilise prefetch_related pour optimiser les requêtes.
    
    Attributs:
        model: Modèle Client
        template_name: Template de liste
        context_object_name: Nom de la variable dans le template
        paginate_by: Nombre d'éléments par page (15 pour les clients)
        
    Fonctionnalités de filtrage:
        - Par type de client (particulier, entreprise, association, administration)
        - Par statut actif/inactif
        - Recherche textuelle (nom, email, ville)
        
    Optimisations:
        - prefetch_related pour charger les factures liées
        - Pagination automatique
        - Tri alphabétique par nom
    """
    model = Client
    template_name = 'django_exo_1/client_list.html'
    context_object_name = 'clients'
    paginate_by = 15
    
    def get_queryset(self):
        """
        Construction du queryset avec filtres et optimisations.
        
        Applique les filtres basés sur les paramètres GET et optimise
        les requêtes avec prefetch_related pour les factures.
        
        Returns:
            QuerySet: Clients filtrés et optimisés, triés par nom
        """
        # Optimisation : précharge les factures liées pour éviter les requêtes N+1
        queryset = Client.objects.prefetch_related('factures')
        
        # Filtrage par type de client
        type_client = self.request.GET.get('type_client')
        if type_client:
            queryset = queryset.filter(type_client=type_client)
        
        # Filtrage par statut actif
        est_actif = self.request.GET.get('est_actif')
        if est_actif:
            queryset = queryset.filter(est_actif=est_actif == 'true')
        
        # Recherche textuelle dans plusieurs champs
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(nom__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(ville__icontains=search)
            )
        
        return queryset.order_by('nom')
    
    def get_context_data(self, **kwargs):
        """
        Ajout de données supplémentaires au contexte du template.
        
        Fournit les choix de types de clients pour le filtrage.
        
        Args:
            **kwargs: Arguments du contexte parent
            
        Returns:
            dict: Contexte enrichi avec les types de clients
        """
        context = super().get_context_data(**kwargs)
        context['types_client'] = Client.TYPE_CHOICES
        return context


class ClientDetailView(DetailView):
    """
    Vue basée sur classe pour afficher le détail d'un client avec ses statistiques.
    
    Affiche toutes les informations d'un client spécifique ainsi que
    ses factures et statistiques commerciales.
    
    Attributs:
        model: Modèle Client
        template_name: Template de détail
        context_object_name: Nom de la variable dans le template ('client')
        
    Fonctionnalités:
        - Affichage complet des informations client
        - Liste des factures du client
        - Statistiques commerciales (CA, nombre de factures)
        - Actions d'édition et suppression
    """
    model = Client
    template_name = 'django_exo_1/client_detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        """
        Enrichissement du contexte avec les factures et statistiques du client.
        
        Calcule les statistiques commerciales du client et récupère
        ses factures triées par date d'émission décroissante.
        
        Args:
            **kwargs: Arguments du contexte parent
            
        Returns:
            dict: Contexte enrichi avec factures et statistiques
        """
        context = super().get_context_data(**kwargs)
        # Récupération du client et de ses factures optimisées
        client = self.get_object()
        factures = client.factures.select_related('categorie').order_by('-date_emission')
        
        # Calcul des statistiques commerciales du client
        from django.db.models import Sum, Count
        stats = client.factures.aggregate(
            total_factures=Count('id'),
            ca_total=Sum('montant_ttc', filter=models.Q(statut='payee')),
            factures_payees=Count('id', filter=models.Q(statut='payee')),
            factures_en_attente=Count('id', filter=models.Q(statut='envoyee')),
        )
        
        context['factures'] = factures
        context['stats'] = stats
        return context


class ClientUpdateView(UpdateView):
    """
    Vue basée sur classe pour modifier un client existant.
    
    Permet la modification de toutes les informations d'un client
    avec les mêmes validations que lors de la création.
    
    Attributs:
        model: Modèle Client
        form_class: ClientForm avec widgets Bootstrap
        template_name: Template de modification
        
    Fonctionnalités:
        - Modification complète des données client
        - Validation des champs obligatoires
        - Redirection vers la page de détail après modification
    """
    model = Client
    form_class = ClientForm
    template_name = 'django_exo_1/client_update.html'
    
    def get_success_url(self):
        """
        URL de redirection après modification réussie.
        
        Returns:
            str: URL de la page de détail du client modifié
        """
        return reverse_lazy('django_exo_1:client_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """
        Traitement lors de la validation réussie du formulaire.
        
        Args:
            form: Formulaire validé avec les nouvelles données
            
        Returns:
            HttpResponse: Redirection vers la page de détail avec message
        """
        messages.success(self.request, 'Le client a été modifié avec succès!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Traitement lors de l'échec de validation du formulaire.
        
        Args:
            form: Formulaire avec erreurs de validation
            
        Returns:
            HttpResponse: Retour au formulaire avec message d'erreur
        """
        messages.error(self.request, 'Erreur lors de la modification du client. Veuillez vérifier les informations saisies.')
        return super().form_invalid(form)


class ClientDeleteView(DeleteView):
    """
    Vue basée sur classe pour supprimer un client.
    
    ATTENTION: La suppression d'un client peut être bloquée s'il a des factures
    associées à cause de la contrainte PROTECT sur la relation.
    
    Attributs:
        model: Modèle Client
        template_name: Template de confirmation de suppression
        success_url: Redirection vers la liste après suppression
        
    Sécurité:
        - Page de confirmation obligatoire
        - Protection contre la suppression si des factures existent
        - Message de succès après suppression
    """
    model = Client
    template_name = 'django_exo_1/client_confirm_delete.html'
    success_url = reverse_lazy('django_exo_1:client_list')
    
    def delete(self, request, *args, **kwargs):
        """
        Traitement de la suppression avec message de confirmation.
        
        Args:
            request: Requête HTTP de suppression
            *args: Arguments positionnels
            **kwargs: Arguments nommés (incluant pk)
            
        Returns:
            HttpResponse: Redirection vers la liste avec message de succès
        """
        messages.success(request, 'Le client a été supprimé avec succès!')
        return super().delete(request, *args, **kwargs)


# ==========================================
# VUES POUR LA GESTION DES CATÉGORIES
# ==========================================

class CategorieCreateView(CreateView):
    """
    Vue basée sur classe pour créer une nouvelle catégorie de facture.
    
    Formulaire simple pour créer des catégories avec nom, description
    et couleur d'affichage.
    
    Attributs:
        model: Modèle CategorieFacture
        form_class: CategorieFactureForm avec sélecteur de couleur
        template_name: Template de création
        success_url: Redirection vers la liste des catégories
        
    Fonctionnalités:
        - Création de catégorie avec validation d'unicité du nom
        - Sélecteur de couleur HTML5
        - Description optionnelle
    """
    model = CategorieFacture
    form_class = CategorieFactureForm
    template_name = 'django_exo_1/categorie_create.html'
    success_url = reverse_lazy('django_exo_1:categorie_list')
    
    def form_valid(self, form):
        """
        Traitement lors de la validation réussie du formulaire.
        
        Args:
            form: Formulaire validé avec les données de la catégorie
            
        Returns:
            HttpResponse: Redirection vers la liste avec message de succès
        """
        messages.success(self.request, 'La catégorie a été créée avec succès!')
        return super().form_valid(form)


class CategorieListView(ListView):
    """
    Vue basée sur classe pour lister toutes les catégories de factures.
    
    Affiche une liste simple de toutes les catégories avec leurs couleurs
    et descriptions. Pas de pagination car le nombre de catégories reste limité.
    
    Attributs:
        model: Modèle CategorieFacture
        template_name: Template de liste
        context_object_name: Nom de la variable dans le template
        
    Fonctionnalités:
        - Liste complète des catégories
        - Affichage des couleurs
        - Actions de création, modification, suppression
    """
    model = CategorieFacture
    template_name = 'django_exo_1/categorie_list.html'
    context_object_name = 'categories'


# ==========================================
# API ET VUES UTILITAIRES
# ==========================================

def client_list_json(request):
    """
    Vue API pour récupérer la liste des clients actifs au format JSON.
    
    Utilisée pour les fonctionnalités AJAX, notamment pour le pré-remplissage
    automatique des informations client dans les formulaires de facture.
    
    Args:
        request (HttpRequest): Requête HTTP (généralement AJAX)
        
    Returns:
        JsonResponse: Liste des clients actifs avec leurs informations formatées
        
    Format de réponse:
        [
            {
                "id": 1,
                "nom": "Nom du client",
                "email": "email@client.com",
                "adresse_complete": "Adresse\nCode postal Ville\nPays"
            },
            ...
        ]
        
    Utilisation:
        - Pré-remplissage des formulaires
        - Sélection dynamique de clients
        - Intégration avec JavaScript côté client
    """
    # Récupération des clients actifs avec les champs nécessaires
    clients = Client.objects.filter(est_actif=True).values(
        'id', 'nom', 'email', 'adresse', 'code_postal', 'ville', 'pays'
    )
    
    # Formatage des données pour l'API
    clients_data = []
    for client in clients:
        clients_data.append({
            'id': client['id'],
            'nom': client['nom'],
            'email': client['email'],
            'adresse_complete': f"{client['adresse']}\n{client['code_postal']} {client['ville']}\n{client['pays']}"
        })
    
    return JsonResponse(clients_data, safe=False)


def facture_bulk_action(request):
    """
    Vue pour traiter les actions de lot sur les factures.
    
    Permet d'effectuer des actions sur plusieurs factures sélectionnées :
    - Marquer comme payées
    - Autres actions possibles à l'avenir
    
    Args:
        request (HttpRequest): Requête HTTP POST avec les factures sélectionnées
        
    Returns:
        HttpResponse: Redirection vers la liste des factures avec message
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_factures = request.POST.getlist('selected_factures')
        
        if not selected_factures:
            messages.error(request, 'Aucune facture sélectionnée.')
            return redirect('django_exo_1:facture_list')
        
        if action == 'mark_paid':
            # Récupérer les factures sélectionnées qui ne sont pas déjà payées
            factures = Facture.objects.filter(
                id__in=selected_factures
            ).non_payees()
            
            if not factures.exists():
                messages.warning(request, 'Toutes les factures sélectionnées sont déjà payées.')
                return redirect('django_exo_1:facture_list')
            
            # Mettre à jour le statut
            updated_count = factures.update(statut='payee')
            
            if updated_count > 0:
                messages.success(
                    request, 
                    f'{updated_count} facture(s) marquée(s) comme payée(s) avec succès!'
                )
            else:
                messages.warning(request, 'Aucune facture n\'a pu être mise à jour.')
        
        else:
            messages.error(request, 'Action non reconnue.')
    
    return redirect('django_exo_1:facture_list')


class LogCreationFactureListView(ListView):
    """
    Vue pour afficher la liste des logs de création de factures.
    
    Permet aux utilisateurs de voir l'historique des créations de factures
    avec toutes les métadonnées enregistrées par le middleware.
    
    Attributs:
        model: Modèle LogCreationFacture
        template_name: Template de liste des logs
        context_object_name: Nom de la variable dans le template
        paginate_by: Nombre d'éléments par page
        ordering: Ordre de tri (plus récent d'abord)
    """
    model = LogCreationFacture
    template_name = 'django_exo_1/log_creation_list.html'
    context_object_name = 'logs'
    paginate_by = 20
    ordering = ['-date_creation']
    
    def get_context_data(self, **kwargs):
        """
        Ajoute des données supplémentaires au contexte.
        
        Returns:
            dict: Contexte enrichi avec statistiques
        """
        context = super().get_context_data(**kwargs)
        
        # Statistiques sur les logs
        total_logs = LogCreationFacture.objects.count()
        logs_today = LogCreationFacture.objects.aujourd_hui().count()
        
        context.update({
            'total_logs': total_logs,
            'logs_today': logs_today,
        })
        
        return context


def dashboard_statistics(request):
    """
    Vue pour afficher un dashboard détaillé avec les managers personnalisés.
    
    Démontre l'utilisation des managers et QuerySets pour simplifier le code.
    """
    # Utilisation des managers personnalisés
    stats = Facture.objects.statistiques()
    
    # Factures à échéance proche (7 jours)
    factures_echeance_proche = Facture.objects.echeance_proche(7).avec_relations()
    
    # Factures en retard
    factures_en_retard = Facture.objects.echeance_passee().avec_relations()
    
    # Top 5 des clients (par nombre de factures)
    from django.db.models import Count
    top_clients = Client.objects.annotate(
        nb_factures=Count('factures')
    ).order_by('-nb_factures')[:5]
    
    # Chiffre d'affaires par catégorie
    from django.db.models import Sum
    ca_par_categorie = CategorieFacture.objects.annotate(
        ca=Sum('facture__montant_ttc', filter=models.Q(facture__statut='payee'))
    ).exclude(ca__isnull=True).order_by('-ca')
    
    context = {
        'stats': stats,
        'factures_echeance_proche': factures_echeance_proche,
        'factures_en_retard': factures_en_retard,
        'top_clients': top_clients,
        'ca_par_categorie': ca_par_categorie,
    }
    
    return render(request, 'django_exo_1/dashboard.html', context)
