# Generated by Django 3.0.3 on 2020-07-20 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0055_filmawardpersonmapping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='awardscategories',
            name='personType',
        ),
    ]
