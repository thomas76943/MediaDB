# Generated by Django 3.0.3 on 2020-07-12 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0031_franchisesubcategory_subcategoryorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='franchise',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
