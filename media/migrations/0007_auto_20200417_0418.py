# Generated by Django 3.0.3 on 2020-04-17 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0006_auto_20200417_0332'),
    ]

    operations = [
        migrations.RenameField(
            model_name='television',
            old_name='epsiodes',
            new_name='episodes',
        ),
        migrations.AlterField(
            model_name='film',
            name='posterFilePath',
            field=models.CharField(default='https://i.gyazo.com/94770d8db3ef2cf193553e34f6e29e2d.png', max_length=500),
        ),
    ]
