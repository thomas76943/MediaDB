# Generated by Django 3.0.3 on 2020-07-12 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0034_person_alive'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='bio',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
