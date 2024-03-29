# Generated by Django 3.0.3 on 2020-08-27 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0074_auto_20200826_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, default='', upload_to='bookCoverImages'),
        ),
        migrations.AlterField(
            model_name='book',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='bookImages'),
        ),
    ]
