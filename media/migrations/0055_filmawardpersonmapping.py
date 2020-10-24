# Generated by Django 3.0.3 on 2020-07-20 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0054_awardscategories_persontype'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmAwardPersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FilmAwardMapping', models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='media.FilmAwardMapping')),
                ('Person', models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
            ],
            options={
                'verbose_name': 'Film - Award Peron Mapping',
                'verbose_name_plural': 'Films - Award Person Mappings ',
            },
        ),
    ]
