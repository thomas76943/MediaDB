# Generated by Django 3.0.3 on 2020-12-17 17:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media', '0108_person_slug'),
        ('users', '0011_auto_20200908_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserListWebSeriesMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
            options={
                'verbose_name': 'User List - Web Series Mapping',
                'verbose_name_plural': 'User List - Web Series Mappings',
            },
        ),
        migrations.CreateModel(
            name='UserListVideoGameMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
            options={
                'verbose_name': 'User List - Video Game Mapping',
                'verbose_name_plural': 'User List - Video Game Mappings',
            },
        ),
        migrations.CreateModel(
            name='UserListTelevisionMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User List - Television Mapping',
                'verbose_name_plural': 'User List - Television Mappings',
            },
        ),
        migrations.CreateModel(
            name='UserListFilmMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User List - Film Mapping',
                'verbose_name_plural': 'User List - Film Mappings',
            },
        ),
        migrations.CreateModel(
            name='UserListBookMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User List - Book Mapping',
                'verbose_name_plural': 'User List - Book Mappings',
            },
        ),
    ]
