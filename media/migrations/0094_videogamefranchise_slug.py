# Generated by Django 3.0.3 on 2020-10-15 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0093_franchise_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='videogamefranchise',
            name='slug',
            field=models.SlugField(blank=True, max_length=150),
        ),
    ]
