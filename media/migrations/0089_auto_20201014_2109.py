# Generated by Django 3.0.3 on 2020-10-14 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0088_auto_20201014_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videogame',
            name='posterFilePath',
            field=models.CharField(blank=True, default='../static/media/MissingIcon.png', max_length=500),
        ),
    ]
