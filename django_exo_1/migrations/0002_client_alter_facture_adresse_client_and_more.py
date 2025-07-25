# Generated by Django 4.2.23 on 2025-07-21 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_exo_1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, verbose_name='Nom/Raison sociale')),
                ('type_client', models.CharField(choices=[('particulier', 'Particulier'), ('entreprise', 'Entreprise'), ('association', 'Association'), ('administration', 'Administration')], default='entreprise', max_length=20, verbose_name='Type de client')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('telephone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Téléphone')),
                ('adresse', models.TextField(verbose_name='Adresse')),
                ('code_postal', models.CharField(max_length=10, verbose_name='Code postal')),
                ('ville', models.CharField(max_length=100, verbose_name='Ville')),
                ('pays', models.CharField(default='France', max_length=100, verbose_name='Pays')),
                ('siret', models.CharField(blank=True, max_length=14, null=True, verbose_name='N° SIRET')),
                ('numero_tva', models.CharField(blank=True, max_length=20, null=True, verbose_name='N° TVA intracommunautaire')),
                ('est_actif', models.BooleanField(default=True, verbose_name='Client actif')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes sur le client')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'ordering': ['nom'],
            },
        ),
        migrations.AlterField(
            model_name='facture',
            name='adresse_client',
            field=models.TextField(blank=True, verbose_name='Adresse du client (override)'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='email_client',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email du client (override)'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='nom_client',
            field=models.CharField(blank=True, max_length=200, verbose_name='Nom du client (override)'),
        ),
        migrations.AddField(
            model_name='facture',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='factures', to='django_exo_1.client', verbose_name='Client'),
        ),
    ]
