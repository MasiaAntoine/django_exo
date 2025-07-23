from django.urls import path
from . import views

app_name = 'django_exo_1'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_statistics, name='dashboard'),
    
    # URLs pour les clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/json/', views.client_list_json, name='client_list_json'),
    path('clients/nouveau/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/modifier/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/supprimer/', views.ClientDeleteView.as_view(), name='client_delete'),
    
    # URLs pour les factures
    path('factures/', views.FactureListView.as_view(), name='facture_list'),
    path('factures/action-lot/', views.facture_bulk_action, name='facture_bulk_action'),
    path('factures/logs/', views.LogCreationFactureListView.as_view(), name='log_creation_list'),
    path('factures/nouvelle/', views.FactureCreateView.as_view(), name='facture_create'),
    path('factures/<int:pk>/', views.FactureDetailView.as_view(), name='facture_detail'),
    path('factures/<int:pk>/modifier/', views.FactureUpdateView.as_view(), name='facture_update'),
    path('factures/<int:pk>/supprimer/', views.FactureDeleteView.as_view(), name='facture_delete'),
    
    # URLs pour les catégories
    path('categories/', views.CategorieListView.as_view(), name='categorie_list'),
    path('categories/nouvelle/', views.CategorieCreateView.as_view(), name='categorie_create'),
]
