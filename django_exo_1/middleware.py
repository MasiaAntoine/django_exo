"""
Middleware pour l'enregistrement des créations de factures.

Ce middleware intercepte toutes les requêtes et détecte les créations de factures
pour les enregistrer automatiquement dans le modèle LogCreationFacture.
"""

import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.http import HttpResponse
from .models import Facture, LogCreationFacture

logger = logging.getLogger(__name__)


class FactureCreationLogMiddleware(MiddlewareMixin):
    """
    Middleware qui enregistre automatiquement toutes les créations de factures.
    
    Ce middleware surveille les requêtes POST vers la vue de création de factures
    et enregistre les informations de création dans la base de données via
    le modèle LogCreationFacture.
    
    Fonctionnalités :
    - Détection automatique des créations de factures
    - Enregistrement des métadonnées de la requête
    - Gestion des erreurs sans interrompre le flux normal
    - Stockage des données POST (sanitisées)
    """
    
    def __init__(self, get_response):
        """
        Initialisation du middleware.
        
        Args:
            get_response: Fonction de traitement de la requête suivante
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Traitement avant l'exécution de la vue.
        
        Stocke les informations de la requête pour pouvoir les utiliser
        après la création de la facture.
        
        Args:
            request: Objet HttpRequest de Django
        """
        # Stocker les informations de la requête pour utilisation ultérieure
        if hasattr(request, 'POST') and request.method == 'POST':
            # Résoudre l'URL pour obtenir le nom de la vue
            try:
                url_match = resolve(request.path_info)
                request._middleware_url_name = url_match.url_name
                request._middleware_app_name = url_match.app_name
            except:
                request._middleware_url_name = None
                request._middleware_app_name = None
        
        return None
    
    def process_response(self, request, response):
        """
        Traitement après l'exécution de la vue.
        
        Détecte si une facture a été créée et enregistre le log correspondant.
        
        Args:
            request: Objet HttpRequest de Django
            response: Objet HttpResponse de Django
            
        Returns:
            HttpResponse: La réponse inchangée
        """
        # Vérifier si c'est une création de facture réussie
        if self._is_facture_creation(request, response):
            try:
                # Trouver la facture nouvellement créée
                facture = self._get_created_facture(request)
                if facture:
                    self._create_log_entry(request, facture)
            except Exception as e:
                # Logger l'erreur mais ne pas interrompre le processus
                logger.error(f"Erreur lors de l'enregistrement du log de création de facture: {e}")
        
        return response
    
    def _is_facture_creation(self, request, response):
        """
        Détermine si la requête correspond à une création de facture réussie.
        
        Args:
            request: Objet HttpRequest
            response: Objet HttpResponse
            
        Returns:
            bool: True si c'est une création de facture réussie
        """
        # Vérifier que c'est une requête POST
        if request.method != 'POST':
            return False
        
        # Vérifier que c'est vers la vue de création de factures
        url_name = getattr(request, '_middleware_url_name', None)
        app_name = getattr(request, '_middleware_app_name', None)
        
        if app_name != 'django_exo_1' or url_name != 'facture_create':
            return False
        
        # Vérifier que la réponse indique un succès (redirection après création)
        if response.status_code != 302:
            return False
        
        return True
    
    def _get_created_facture(self, request):
        """
        Récupère la facture qui vient d'être créée.
        
        Utilise le numéro de facture du POST pour identifier la facture créée.
        
        Args:
            request: Objet HttpRequest
            
        Returns:
            Facture: La facture créée ou None
        """
        try:
            numero_facture = request.POST.get('numero')
            if numero_facture:
                # Récupérer la facture créée le plus récemment avec ce numéro
                return Facture.objects.filter(numero=numero_facture).order_by('-date_creation').first()
        except Exception as e:
            logger.warning(f"Impossible de récupérer la facture créée: {e}")
        
        return None
    
    def _create_log_entry(self, request, facture):
        """
        Crée une entrée de log pour la création de facture.
        
        Args:
            request: Objet HttpRequest
            facture: Instance de Facture créée
        """
        try:
            # Extraire les métadonnées de la requête
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = self._get_client_ip(request)
            referer = request.META.get('HTTP_REFERER')
            session_key = request.session.session_key if hasattr(request, 'session') else None
            
            # Préparer les données POST (en excluant les données sensibles)
            donnees_post = self._sanitize_post_data(request.POST.dict())
            
            # Créer l'entrée de log
            LogCreationFacture.objects.create(
                facture=facture,
                user_agent=user_agent,
                ip_address=ip_address,
                referer=referer,
                session_key=session_key,
                methode_http=request.method,
                donnees_post=donnees_post
            )
            
            logger.info(f"Log de création enregistré pour la facture {facture.numero}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du log: {e}")
    
    def _get_client_ip(self, request):
        """
        Extrait l'adresse IP du client de la requête.
        
        Gère les cas de proxy et load balancer.
        
        Args:
            request: Objet HttpRequest
            
        Returns:
            str: Adresse IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Prendre la première IP (client réel) en cas de proxy multiple
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
    
    def _sanitize_post_data(self, post_data):
        """
        Nettoie les données POST en supprimant les informations sensibles.
        
        Args:
            post_data: Dictionnaire des données POST
            
        Returns:
            dict: Données POST nettoyées
        """
        # Champs à exclure pour des raisons de sécurité
        champs_sensibles = [
            'csrfmiddlewaretoken',
            'password',
            'token',
            'session',
            'auth'
        ]
        
        return {
            key: value for key, value in post_data.items()
            if not any(sensible in key.lower() for sensible in champs_sensibles)
        }
