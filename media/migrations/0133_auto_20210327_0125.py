# Generated by Django 3.0.3 on 2021-03-27 01:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0132_auto_20210325_0941'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='highestratedbooks',
            options={'verbose_name': 'Highest Rated Book', 'verbose_name_plural': 'Highest Rated Books'},
        ),
        migrations.AlterField(
            model_name='film',
            name='slug',
            field=models.SlugField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='videogamevideogamefranchisesubcategorymapping',
            name='videoGame',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.VideoGame'),
        ),
    ]
