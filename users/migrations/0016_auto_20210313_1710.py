# Generated by Django 3.0.3 on 2021-03-13 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_profilesection_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesection',
            name='sectionName',
            field=models.CharField(default='Profile Section', max_length=20),
        ),
        migrations.AlterField(
            model_name='profilesection',
            name='type',
            field=models.CharField(default='Films', max_length=10),
        ),
    ]
