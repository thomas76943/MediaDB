# Generated by Django 3.0.3 on 2020-09-01 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0078_auto_20200901_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='cover',
            field=models.ImageField(blank=True, default='', upload_to='coverImages'),
        ),
    ]
