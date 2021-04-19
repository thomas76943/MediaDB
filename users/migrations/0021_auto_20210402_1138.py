# Generated by Django 3.0.3 on 2021-04-02 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20210402_1135'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filmrecommendations',
            options={'verbose_name': 'User - Film Recommendation', 'verbose_name_plural': 'User - Film Recommendations'},
        ),
        migrations.AlterField(
            model_name='filmrecommendations',
            name='films',
            field=models.TextField(default='', max_length=250),
        ),
    ]