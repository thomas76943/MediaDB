# Generated by Django 3.0.3 on 2021-01-28 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_userlistbookmapping_userlistfilmmapping_userlisttelevisionmapping_userlistvideogamemapping_userlistw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(null=True, upload_to='profile_pics'),
        ),
    ]
