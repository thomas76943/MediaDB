# Generated by Django 3.0.3 on 2021-03-19 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0121_auto_20210319_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filmimages',
            name='filePath',
        ),
        migrations.RemoveField(
            model_name='miscimages',
            name='filePath',
        ),
        migrations.RemoveField(
            model_name='televisionimages',
            name='filePath',
        ),
        migrations.RemoveField(
            model_name='videogameimages',
            name='filePath',
        ),
        migrations.RemoveField(
            model_name='webseriesimages',
            name='filePath',
        ),
    ]
