# Generated by Django 3.0.3 on 2021-02-03 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0112_auto_20210202_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='franchise',
            name='showPeople',
            field=models.BooleanField(default=False),
        ),
    ]
