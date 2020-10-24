# Generated by Django 3.0.3 on 2020-08-24 15:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0068_auto_20200820_1809'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20200824_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebSeriesRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=1)),
                ('dateTime', models.DateTimeField(default=django.utils.datetime_safe.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
            options={
                'verbose_name': 'Web Series - Rating',
                'verbose_name_plural': 'Web Series - Ratings',
            },
        ),
        migrations.CreateModel(
            name='VideoGameRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=1)),
                ('dateTime', models.DateTimeField(default=django.utils.datetime_safe.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
            options={
                'verbose_name': 'Video Game - Rating',
                'verbose_name_plural': 'Video Games - Ratings',
            },
        ),
        migrations.CreateModel(
            name='BookRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=1)),
                ('dateTime', models.DateTimeField(default=django.utils.datetime_safe.datetime.now)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Book - Rating',
                'verbose_name_plural': 'Books - Ratings',
            },
        ),
    ]
