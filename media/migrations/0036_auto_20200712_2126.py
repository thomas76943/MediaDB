# Generated by Django 3.0.3 on 2020-07-12 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0035_person_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='bio',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
