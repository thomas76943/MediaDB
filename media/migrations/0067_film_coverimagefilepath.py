# Generated by Django 3.0.3 on 2020-08-20 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0066_auto_20200819_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='coverImageFilePath',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
