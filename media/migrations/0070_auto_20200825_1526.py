# Generated by Django 3.0.3 on 2020-08-25 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0069_person_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='personimages',
            name='image',
            field=models.ImageField(blank=True, default='MissingIcon.png', upload_to='people'),
        ),
        migrations.AlterField(
            model_name='miscimages',
            name='filePath',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='personimages',
            name='filePath',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
