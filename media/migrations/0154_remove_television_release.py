# Generated by Django 3.0.3 on 2025-01-27 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0153_auto_20250127_1054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='television',
            name='release',
        ),
    ]
