# Generated by Django 4.2.23 on 2025-07-22 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_exo_1', '0004_remove_client_override_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogCreationFacture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent', models.TextField(blank=True, help_text='Informations sur le navigateur utilisé', null=True, verbose_name='User Agent')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text="Adresse IP de l'utilisateur", null=True, verbose_name='Adresse IP')),
                ('referer', models.URLField(blank=True, help_text='URL de la page depuis laquelle la création a été initiée', null=True, verbose_name='Page de référence')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création du log')),
                ('session_key', models.CharField(blank=True, help_text='Identifiant de session Django', max_length=40, null=True, verbose_name='Clé de session')),
                ('methode_http', models.CharField(default='POST', max_length=10, verbose_name='Méthode HTTP')),
                ('donnees_post', models.JSONField(blank=True, help_text='Données du formulaire utilisé pour créer la facture', null=True, verbose_name='Données POST')),
                ('facture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs_creation', to='django_exo_1.facture', verbose_name='Facture créée')),
            ],
            options={
                'verbose_name': 'Log de création de facture',
                'verbose_name_plural': 'Logs de création de factures',
                'ordering': ['-date_creation'],
                'indexes': [models.Index(fields=['date_creation'], name='django_exo__date_cr_962ff6_idx'), models.Index(fields=['facture'], name='django_exo__facture_e973ec_idx'), models.Index(fields=['ip_address'], name='django_exo__ip_addr_9ef84c_idx')],
            },
        ),
    ]
