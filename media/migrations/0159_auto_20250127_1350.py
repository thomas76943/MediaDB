# Generated by Django 3.0.3 on 2025-01-27 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0158_auto_20250127_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='televisionepisode',
            options={'verbose_name': 'Television - Episode', 'verbose_name_plural': 'Television - Episodes'},
        ),
        migrations.AlterModelOptions(
            name='televisionseason',
            options={'verbose_name': 'Television - Season', 'verbose_name_plural': 'Television - Seasons'},
        ),
        migrations.AddField(
            model_name='televisionpersonmapping',
            name='episodes',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.CreateModel(
            name='TelevisionEpisodePersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character', models.CharField(blank=True, default='', max_length=500)),
                ('billing', models.IntegerField(default=1)),
                ('department', models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='media.Department')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.PersonRole')),
                ('televisionEpisode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.TelevisionEpisode')),
            ],
            options={
                'verbose_name': 'Television Episode - Person Mapping',
                'verbose_name_plural': 'Television Episode - Person Mappings',
            },
        ),
    ]
