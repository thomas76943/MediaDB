# Generated by Django 3.0.3 on 2025-01-27 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0154_remove_television_release'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='television',
            name='end',
        ),
        migrations.RemoveField(
            model_name='television',
            name='trailerVideoPath',
        ),
    ]
