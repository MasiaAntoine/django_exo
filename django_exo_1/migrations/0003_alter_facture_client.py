# Generated by Django 4.2.23 on 2025-07-21 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_exo_1', '0002_client_alter_facture_adresse_client_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='factures', to='django_exo_1.client', verbose_name='Client'),
        ),
    ]
