# Generated by Django 3.0.3 on 2020-08-19 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0065_videogamefranchisesubcategory_subcategoryorder'),
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
