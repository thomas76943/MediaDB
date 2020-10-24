# Generated by Django 3.0.3 on 2020-07-20 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0043_auto_20200715_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwardType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
            ],
            options={
                'verbose_name': 'Award',
                'verbose_name_plural': 'Awards',
            },
        ),
        migrations.CreateModel(
            name='WebSeriesAwardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.AwardType')),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
            options={
                'verbose_name': 'Web Series - Award',
                'verbose_name_plural': 'Web Series - Awards',
            },
        ),
        migrations.CreateModel(
            name='VideoGameAwardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.AwardType')),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
            options={
                'verbose_name': 'Video Game - Award',
                'verbose_name_plural': 'Video Games - Awards',
            },
        ),
        migrations.CreateModel(
            name='TelevisionAwardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.AwardType')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
            ],
            options={
                'verbose_name': 'Television - Award',
                'verbose_name_plural': 'Television - Awards',
            },
        ),
        migrations.CreateModel(
            name='FilmAwardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.AwardType')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
            ],
            options={
                'verbose_name': 'Film - Award',
                'verbose_name_plural': 'Films - Awards',
            },
        ),
        migrations.CreateModel(
            name='BookAwardMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=100)),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.AwardType')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
            ],
            options={
                'verbose_name': 'Book - Award',
                'verbose_name_plural': 'Books - Awards',
            },
        ),
    ]
