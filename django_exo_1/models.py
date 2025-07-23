from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.


class FactureQuerySet(models.QuerySet):
    """
    QuerySet personnalisé pour le modèle Facture.
    
    Fournit des méthodes de filtrage courantes pour simplifier les requêtes.
    """
    
    def payees(self):
        """Retourne les factures payées."""
        return self.filter(statut='payee')
    
    def en_attente(self):
        """Retourne les factures en attente (envoyées mais non payées)."""
        return self.filter(statut='envoyee')
    
    def brouillons(self):
        """Retourne les factures en brouillon."""
        return self.filter(statut='brouillon')
    
    def annulees(self):
        """Retourne les factures annulées."""
        return self.filter(statut='annulee')
    
    def non_payees(self):
        """Retourne les factures non payées (brouillon + envoyées)."""
        return self.exclude(statut__in=['payee', 'annulee'])
    
    def par_client(self, client):
        """Filtre par client."""
        return self.filter(client=client)
    
    def par_categorie(self, categorie):
        """Filtre par catégorie."""
        return self.filter(categorie=categorie)
    
    def avec_montant_min(self, montant):
        """Filtre les factures avec un montant TTC minimum."""
        return self.filter(montant_ttc__gte=montant)
    
    def avec_montant_max(self, montant):
        """Filtre les factures avec un montant TTC maximum."""
        return self.filter(montant_ttc__lte=montant)
    
    def echeance_passee(self):
        """Retourne les factures dont l'échéance est dépassée."""
        from django.utils import timezone
        return self.filter(date_echeance__lt=timezone.now().date())
    
    def echeance_proche(self, jours=7):
        """Retourne les factures dont l'échéance arrive dans X jours."""
        from django.utils import timezone
        from datetime import timedelta
        date_limite = timezone.now().date() + timedelta(days=jours)
        return self.filter(date_echeance__lte=date_limite, statut='envoyee')
    
    def par_periode(self, date_debut, date_fin):
        """Filtre par période d'émission."""
        return self.filter(date_emission__range=[date_debut, date_fin])
    
    def recherche(self, terme):
        """Recherche textuelle dans numéro, client et description."""
        return self.filter(
            models.Q(numero__icontains=terme) |
            models.Q(client__nom__icontains=terme) |
            models.Q(client__email__icontains=terme) |
            models.Q(description__icontains=terme)
        )
    
    def avec_relations(self):
        """Optimise les requêtes en chargeant les relations."""
        return self.select_related('client', 'categorie')
    
    def chiffre_affaires(self):
        """Calcule le chiffre d'affaires des factures payées."""
        return self.payees().aggregate(
            total=models.Sum('montant_ttc')
        )['total'] or 0


class FactureManager(models.Manager):
    """
    Manager personnalisé pour le modèle Facture.
    
    Utilise FactureQuerySet pour fournir des méthodes de requête simplifiées.
    """
    
    def get_queryset(self):
        """Retourne le QuerySet personnalisé."""
        return FactureQuerySet(self.model, using=self._db)
    
    def payees(self):
        """Raccourci pour les factures payées."""
        return self.get_queryset().payees()
    
    def en_attente(self):
        """Raccourci pour les factures en attente."""
        return self.get_queryset().en_attente()
    
    def brouillons(self):
        """Raccourci pour les factures brouillons."""
        return self.get_queryset().brouillons()
    
    def non_payees(self):
        """Raccourci pour les factures non payées."""
        return self.get_queryset().non_payees()
    
    def echeance_passee(self):
        """Raccourci pour les factures en retard."""
        return self.get_queryset().echeance_passee()
    
    def echeance_proche(self, jours=7):
        """Raccourci pour les factures à échéance proche."""
        return self.get_queryset().echeance_proche(jours)
    
    def recherche(self, terme):
        """Raccourci pour la recherche textuelle."""
        return self.get_queryset().recherche(terme)
    
    def avec_relations(self):
        """Raccourci pour charger les relations."""
        return self.get_queryset().avec_relations()
    
    def chiffre_affaires(self):
        """Raccourci pour calculer le chiffre d'affaires."""
        return self.get_queryset().chiffre_affaires()
    
    def statistiques(self):
        """Retourne des statistiques globales."""
        return {
            'total': self.count(),
            'payees': self.payees().count(),
            'en_attente': self.en_attente().count(),
            'brouillons': self.brouillons().count(),
            'annulees': self.get_queryset().annulees().count(),
            'en_retard': self.echeance_passee().count(),
            'chiffre_affaires': self.chiffre_affaires(),
        }


class Client(models.Model):
    """
    Modèle représentant un client de l'entreprise.
    
    Un client peut être un particulier, une entreprise, une association ou une administration.
    Il contient toutes les informations nécessaires pour la facturation et le contact.
    
    Attributs:
        nom (CharField): Nom complet ou raison sociale du client
        type_client (CharField): Type de client avec choix prédéfinis
        email (EmailField): Adresse email principale du client
        telephone (CharField): Numéro de téléphone (optionnel)
        adresse (TextField): Adresse complète du client
        code_postal (CharField): Code postal
        ville (CharField): Ville
        pays (CharField): Pays (France par défaut)
        siret (CharField): Numéro SIRET pour les entreprises (optionnel)
        numero_tva (CharField): Numéro de TVA intracommunautaire (optionnel)
        est_actif (BooleanField): Indique si le client est actif
        notes (TextField): Notes libres sur le client (optionnel)
        date_creation (DateTimeField): Date de création automatique
        date_modification (DateTimeField): Date de modification automatique
    
    Relations:
        factures: Toutes les factures liées à ce client (relation inverse)
    """
    
    # Types de clients possibles
    # Utilise des choix pour limiter les valeurs et assurer la cohérence
    TYPE_CHOICES = [
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('association', 'Association'),
        ('administration', 'Administration'),
    ]
    
    # Informations principales
    nom = models.CharField(max_length=200, verbose_name="Nom/Raison sociale")
    type_client = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='entreprise',
        verbose_name="Type de client"
    )
    
    # Coordonnées
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    adresse = models.TextField(verbose_name="Adresse")
    code_postal = models.CharField(max_length=10, verbose_name="Code postal")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=100, default="France", verbose_name="Pays")
    
    # Informations entreprise (optionnelles)
    siret = models.CharField(max_length=14, blank=True, null=True, verbose_name="N° SIRET")
    numero_tva = models.CharField(max_length=20, blank=True, null=True, verbose_name="N° TVA intracommunautaire")
    
    # Informations commerciales
    est_actif = models.BooleanField(default=True, verbose_name="Client actif")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes sur le client")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom']
    
    def __str__(self):
        """
        Représentation textuelle du client.
        
        Returns:
            str: Le nom/raison sociale du client
        """
        return self.nom
    
    @property
    def adresse_complete(self):
        """
        Propriété calculée qui retourne l'adresse complète formatée.
        
        Combine l'adresse, le code postal, la ville et le pays sur plusieurs lignes.
        Utilisée pour l'affichage sur les factures et documents.
        
        Returns:
            str: Adresse complète formatée avec sauts de ligne
        """
        return f"{self.adresse}\n{self.code_postal} {self.ville}\n{self.pays}"


class CategorieFacture(models.Model):
    """
    Modèle représentant une catégorie de facture.
    
    Permet de classer les factures par type (Services, Produits, Consulting, etc.).
    Chaque catégorie a une couleur associée pour l'affichage visuel.
    
    Attributs:
        nom (CharField): Nom unique de la catégorie
        description (TextField): Description détaillée (optionnel)
        couleur (CharField): Code couleur hexadécimal pour l'affichage
        date_creation (DateTimeField): Date de création automatique
    
    Relations:
        factures: Toutes les factures de cette catégorie (relation inverse via Facture.categorie)
    """
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#007bff", verbose_name="Couleur (hex)", help_text="Couleur au format hexadécimal (#RRGGBB)")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Catégorie de facture"
        verbose_name_plural = "Catégories de factures"
        ordering = ['nom']
    
    def __str__(self):
        """
        Représentation textuelle de la catégorie.
        
        Returns:
            str: Le nom de la catégorie
        """
        return self.nom


class Facture(models.Model):
    """
    Modèle principal représentant une facture.
    
    Une facture est associée à un client et une catégorie.
    Elle contient tous les montants (HT, TVA, TTC) avec calcul automatique du TTC.
    
    Attributs:
        numero (CharField): Numéro unique de la facture
        date_emission (DateField): Date d'émission de la facture
        date_echeance (DateField): Date limite de paiement
        client (ForeignKey): Client associé à cette facture
        montant_ht (DecimalField): Montant hors taxes (minimum 0.01€)
        taux_tva (DecimalField): Taux de TVA en pourcentage (20% par défaut)
        montant_ttc (DecimalField): Montant toutes taxes comprises (calculé automatiquement)
        categorie (ForeignKey): Catégorie de la facture
        statut (CharField): Statut avec choix prédéfinis (brouillon par défaut)
        description (TextField): Description ou objet de la facture
        notes (TextField): Notes internes (optionnel)
        date_creation (DateTimeField): Date de création automatique
        date_modification (DateTimeField): Date de modification automatique
    
    Relations:
        client: Client associé à cette facture
        categorie: Catégorie de cette facture
    
    Méthodes:
        save(): Calcule automatiquement le montant TTC avant sauvegarde
        montant_tva (property): Calcule le montant de la TVA
    """
    
    # Choix possibles pour le statut de la facture
    # Workflow : brouillon -> envoyée -> payée (ou annulée)
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    # Informations principales
    numero = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    
    # Client (relation avec le modèle Client)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        verbose_name="Client",
        related_name="factures"
    )
    
    # Montants
    montant_ht = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant HT"
    )
    taux_tva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('20.00'),
        verbose_name="Taux TVA (%)"
    )
    montant_ttc = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        editable=False,
        verbose_name="Montant TTC"
    )
    
    # Catégorie et statut
    categorie = models.ForeignKey(
        CategorieFacture, 
        on_delete=models.PROTECT, 
        verbose_name="Catégorie"
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='brouillon',
        verbose_name="Statut"
    )
    
    # Informations complémentaires
    description = models.TextField(verbose_name="Description/Objet de la facture")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes internes")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    objects = FactureManager()  # Utilisation du manager personnalisé
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission', '-numero']
    
    def save(self, *args, **kwargs):
        """
        Méthode de sauvegarde personnalisée.
        
        Calcule automatiquement le montant TTC à partir du montant HT et du taux de TVA
        avant de sauvegarder en base de données.
        
        Formule: montant_ttc = montant_ht * (1 + taux_tva / 100)
        
        Args:
            *args: Arguments positionnels passés à la méthode save() parente
            **kwargs: Arguments nommés passés à la méthode save() parente
        """
        self.montant_ttc = self.montant_ht * (1 + self.taux_tva / 100)
        super().save(*args, **kwargs)
    
    def __str__(self):
        """
        Représentation textuelle de la facture.
        
        Returns:
            str: Format "Facture {numero} - {nom_client}"
        """
        return f"Facture {self.numero} - {self.client.nom}"
    
    @property
    def montant_tva(self):
        """
        Propriété calculée qui retourne le montant de la TVA.
        
        Calcule la différence entre le montant TTC et le montant HT.
        Utilisée pour l'affichage détaillé des montants sur les factures.
        
        Returns:
            Decimal: Montant de la TVA en euros
        """
        return self.montant_ttc - self.montant_ht


class LogCreationFactureQuerySet(models.QuerySet):
    """
    QuerySet personnalisé pour le modèle LogCreationFacture.
    """
    
    def par_date(self, date):
        """Filtre les logs par date."""
        return self.filter(date_creation__date=date)
    
    def aujourd_hui(self):
        """Retourne les logs d'aujourd'hui."""
        from django.utils import timezone
        return self.par_date(timezone.now().date())
    
    def par_facture(self, facture):
        """Filtre par facture."""
        return self.filter(facture=facture)
    
    def par_ip(self, ip):
        """Filtre par adresse IP."""
        return self.filter(ip_address=ip)


class LogCreationFactureManager(models.Manager):
    """
    Manager personnalisé pour LogCreationFacture.
    """
    
    def get_queryset(self):
        return LogCreationFactureQuerySet(self.model, using=self._db)
    
    def aujourd_hui(self):
        return self.get_queryset().aujourd_hui()
    
    def par_date(self, date):
        return self.get_queryset().par_date(date)


class LogCreationFacture(models.Model):
    """
    Modèle pour enregistrer les logs de création de factures.
    
    Ce modèle stocke toutes les informations relatives à la création d'une facture,
    incluant l'utilisateur qui l'a créée, l'heure de création, l'adresse IP, etc.
    Utilisé par le middleware FactureCreationLogMiddleware.
    """
    
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        verbose_name="Facture créée",
        related_name="logs_creation"
    )
    
    # Informations sur la requête HTTP
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="Informations sur le navigateur utilisé"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP de l'utilisateur"
    )
    
    referer = models.URLField(
        blank=True,
        null=True,
        verbose_name="Page de référence",
        help_text="URL de la page depuis laquelle la création a été initiée"
    )
    
    # Informations temporelles
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création du log"
    )
    
    # Informations de session
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name="Clé de session",
        help_text="Identifiant de session Django"
    )
    
    # Informations techniques
    methode_http = models.CharField(
        max_length=10,
        default="POST",
        verbose_name="Méthode HTTP"
    )
    
    # Données supplémentaires (stockage JSON pour flexibilité)
    donnees_post = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Données POST",
        help_text="Données du formulaire utilisé pour créer la facture"
    )
    
    objects = LogCreationFactureManager()  # Manager personnalisé
    
    class Meta:
        verbose_name = "Log de création de facture"
        verbose_name_plural = "Logs de création de factures"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['date_creation']),
            models.Index(fields=['facture']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        """
        Représentation textuelle du log.
        """
        return f"Log création {self.facture.numero} - {self.date_creation.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def donnees_sanitisees(self):
        """
        Propriété qui retourne les données POST en excluant les champs sensibles.
        """
        if not self.donnees_post:
            return {}
        
        # Champs à exclure pour la sécurité
        champs_sensibles = ['csrfmiddlewaretoken', 'password', 'token']
        
        return {
            key: value for key, value in self.donnees_post.items()
            if key not in champs_sensibles
        }
