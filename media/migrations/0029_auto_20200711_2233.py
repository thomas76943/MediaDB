# Generated by Django 3.0.3 on 2020-07-11 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0028_auto_20200711_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookfranchisemapping',
            name='orderInFranchise',
        ),
        migrations.RemoveField(
            model_name='filmfranchisemapping',
            name='orderInFranchise',
        ),
        migrations.RemoveField(
            model_name='televisionfranchisemapping',
            name='orderInFranchise',
        ),
        migrations.RemoveField(
            model_name='videogamefranchisemapping',
            name='orderInFranchise',
        ),
        migrations.RemoveField(
            model_name='webseriesfranchisemapping',
            name='orderInFranchise',
        ),
    ]
