# Generated by Django 3.0.3 on 2020-04-15 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0004_auto_20200415_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='television',
            name='seasons',
            field=models.IntegerField(default=1),
        ),
    ]
