# Generated by Django 3.0.3 on 2021-04-14 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0137_auto_20210414_1022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='releaseYear',
            new_name='release',
        ),
    ]
