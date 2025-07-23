from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Client, Facture, CategorieFacture


class ClientForm(forms.ModelForm):
    """
    Formulaire pour la création et modification de clients.
    
    Utilise un ModelForm Django pour générer automatiquement les champs
    à partir du modèle Client. Inclut une personnalisation des widgets
    pour améliorer l'interface utilisateur avec Bootstrap.
    
    Attributs:
        model: Modèle Client associé
        fields: Liste des champs à inclure dans le formulaire
        widgets: Personnalisation de l'affichage des champs avec CSS Bootstrap
    
    Validation:
        Hérite de la validation automatique de Django ModelForm
        Validation de l'email, des champs requis, etc.
    """
    
    class Meta:
        model = Client
        fields = [
            'nom', 'type_client', 'email', 'telephone',
            'adresse', 'code_postal', 'ville', 'pays',
            'siret', 'numero_tva', 'est_actif', 'notes'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet ou raison sociale'
            }),
            'type_client': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '01 23 45 67 89'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète'
            }),
            'code_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '75001'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paris'
            }),
            'pays': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'siret': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678901234'
            }),
            'numero_tva': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'FR12345678901'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur le client...'
            }),
        }


class FactureForm(forms.ModelForm):
    """
    Formulaire pour la création et modification de factures.
    
    Formulaire complexe qui gère la création de factures avec validation
    personnalisée des dates et attribution automatique d'une catégorie "Autres"
    si aucune catégorie n'est sélectionnée.
    
    Attributs:
        model: Modèle Facture associé
        fields: Champs inclus (sans catégorie car elle devient optionnelle)
        widgets: Personnalisation Bootstrap avec types HTML5 (date, number)
    
    Fonctionnalités spéciales:
        - Validation que la date d'échéance est postérieure à la date d'émission
        - Validation de l'unicité du numéro de facture
        - Attribution automatique de la catégorie "Autres" si non spécifiée
        - Pré-remplissage des dates et du taux de TVA pour les nouvelles factures
    """
    """Formulaire pour la création et modification de factures"""
    
    class Meta:
        model = Facture
        fields = [
            'numero', 'date_emission', 'date_echeance', 
            'client', 'montant_ht', 'taux_tva', 'categorie', 'statut',
            'description', 'notes'
        ]
        widgets = {
            'date_emission': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_echeance': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: FACT-2024-001'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control'
            }),
            'montant_ht': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'taux_tva': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la prestation ou du produit'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes internes (optionnel)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialisation du formulaire avec configuration personnalisée.
        
        Configure les valeurs par défaut pour les nouvelles factures et
        définit quels champs sont obligatoires. La catégorie devient optionnelle
        car elle sera assignée automatiquement si non fournie.
        
        Args:
            *args: Arguments positionnels du formulaire
            **kwargs: Arguments nommés du formulaire
        """
        super().__init__(*args, **kwargs)
        # Définir des valeurs par défaut pour les nouvelles factures
        if not self.instance.pk:  # Nouveau formulaire
            self.fields['date_emission'].initial = date.today()
            self.fields['date_echeance'].initial = date.today() + timedelta(days=30)
            self.fields['taux_tva'].initial = 20.00
        
        # Marquer les champs obligatoires (catégorie devient optionnelle)
        required_fields = ['numero', 'date_emission', 'date_echeance', 
                          'client', 'montant_ht', 'description']
        for field_name in required_fields:
            self.fields[field_name].required = True
        
        # Catégorie optionnelle avec gestion automatique
        self.fields['categorie'].required = False
        self.fields['categorie'].empty_label = "Sélectionner une catégorie (optionnel)"
    
    def clean_date_echeance(self):
        """
        Validation personnalisée de la date d'échéance.
        
        Vérifie que la date d'échéance n'est pas antérieure à la date d'émission.
        Cette méthode est appelée automatiquement par Django lors de la validation.
        
        Returns:
            date: La date d'échéance validée
            
        Raises:
            ValidationError: Si la date d'échéance est antérieure à la date d'émission
        """
        date_emission = self.cleaned_data.get('date_emission')
        date_echeance = self.cleaned_data.get('date_echeance')
        
        if date_emission and date_echeance:
            if date_echeance < date_emission:
                raise ValidationError(
                    "La date d'échéance ne peut pas être antérieure à la date d'émission."
                )
        
        return date_echeance
    
    def clean_numero(self):
        """
        Validation personnalisée du numéro de facture.
        
        Vérifie l'unicité du numéro de facture. Permet la modification d'une facture
        existante en gardant le même numéro, mais empêche la création d'une nouvelle
        facture avec un numéro déjà utilisé.
        
        Returns:
            str: Le numéro de facture validé
            
        Raises:
            ValidationError: Si le numéro existe déjà pour une autre facture
        """
        numero = self.cleaned_data.get('numero')
        
        if numero:
            # Vérifier l'unicité seulement si c'est une nouvelle facture
            # ou si le numéro a été modifié
            existing_facture = Facture.objects.filter(numero=numero).first()
            if existing_facture and existing_facture.pk != self.instance.pk:
                raise ValidationError(
                    "Une facture avec ce numéro existe déjà."
                )
        
        return numero
    
    def clean_categorie(self):
        """
        Validation et assignation automatique de la catégorie.
        
        Si aucune catégorie n'est sélectionnée, crée ou récupère automatiquement
        la catégorie "Autres" et l'assigne à la facture. Cela garantit qu'aucune
        facture ne reste sans catégorie.
        
        Returns:
            CategorieFacture: La catégorie assignée à la facture
        """
        categorie = self.cleaned_data.get('categorie')
        
        if not categorie:
            # Créer ou récupérer la catégorie "Autres"
            categorie, created = CategorieFacture.objects.get_or_create(
                nom='Autres',
                defaults={
                    'description': 'Catégorie par défaut pour les factures non classées',
                    'couleur': '#6c757d'  # Couleur grise Bootstrap
                }
            )
        
        return categorie


class CategorieFactureForm(forms.ModelForm):
    """
    Formulaire pour la création et modification de catégories de factures.
    
    Formulaire simple pour gérer les catégories avec personnalisation
    de l'interface utilisateur. Inclut un sélecteur de couleur HTML5.
    
    Attributs:
        model: Modèle CategorieFacture associé
        fields: Tous les champs de la catégorie (nom, description, couleur)
        widgets: Personnalisation Bootstrap avec input color pour la couleur
    
    Fonctionnalités:
        - Validation automatique de l'unicité du nom
        - Sélecteur de couleur HTML5
        - Champ nom obligatoire configuré dans __init__
    """
    
    class Meta:
        model = CategorieFacture
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Services, Produits, Consulting...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie (optionnel)'
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialisation du formulaire de catégorie.
        
        Configure le champ nom comme obligatoire.
        
        Args:
            *args: Arguments positionnels du formulaire
            **kwargs: Arguments nommés du formulaire
        """
        super().__init__(*args, **kwargs)
        self.fields['nom'].required = True
