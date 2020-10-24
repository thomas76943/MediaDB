# Generated by Django 3.0.3 on 2020-07-21 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0060_auto_20200721_1547'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiscImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filePath', models.CharField(default='', max_length=500)),
                ('awardsShow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='media.AwardsShow')),
            ],
            options={
                'verbose_name': 'Misc - Additional Image',
                'verbose_name_plural': 'Misc - Additional Images',
            },
        ),
    ]
