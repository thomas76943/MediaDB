# Generated by Django 3.0.3 on 2025-01-27 10:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0150_auto_20250123_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='television',
            name='tmdbid',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='image',
            field=models.ImageField(blank=True, default='MissingIcon.png', upload_to='peopleImages'),
        ),
        migrations.AlterField(
            model_name='person',
            name='imageSmall',
            field=models.ImageField(blank=True, default='MissingIcon.png', null=True, upload_to='peopleImages'),
        ),
        migrations.CreateModel(
            name='TelevisionSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('release', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('synopsis', models.CharField(blank=True, max_length=500, null=True)),
                ('seasonNmber', models.IntegerField(default=1)),
                ('episodeNumber', models.IntegerField(default=1)),
                ('trailerVideoPath', models.CharField(blank=True, max_length=500, null=True)),
                ('poster', models.ImageField(blank=True, default='', null=True, upload_to='televisionPosters')),
                ('cover', models.ImageField(blank=True, default='', null=True, upload_to='televisionCoverImages')),
                ('slug', models.SlugField(blank=True, max_length=150)),
                ('tmdbid', models.CharField(blank=True, max_length=20, null=True)),
                ('televisionSeries', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='media.Television')),
            ],
            options={
                'verbose_name': 'Television Season',
                'verbose_name_plural': 'Television Seasons',
            },
        ),
        migrations.CreateModel(
            name='TelevisionEpisode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoTelevisionEpisodeTitleSpecified', max_length=500)),
                ('episodeNumber', models.IntegerField(default=1)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('synopsis', models.CharField(blank=True, default='', max_length=500)),
                ('trailerVideoPath', models.CharField(blank=True, default='', max_length=500)),
                ('poster', models.ImageField(blank=True, default='', upload_to='televisionPosters')),
                ('cover', models.ImageField(blank=True, default='', upload_to='televisionCoverImages')),
                ('slug', models.SlugField(blank=True, max_length=150)),
                ('tmdbid', models.CharField(blank=True, max_length=20, null=True)),
                ('televisionSeason', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='media.TelevisionSeason')),
            ],
            options={
                'verbose_name': 'Television Episode',
                'verbose_name_plural': 'Television Episodes',
            },
        ),
    ]
