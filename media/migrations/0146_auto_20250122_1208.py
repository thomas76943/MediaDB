# Generated by Django 3.0.3 on 2025-01-22 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0145_auto_20250122_0916'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': 'Person - Department', 'verbose_name_plural': 'People - Departments'},
        ),
        migrations.AddField(
            model_name='company',
            name='description',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='company',
            name='parentCompany',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='media.Company'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(default='NoCompanyNameSpecified', max_length=500),
        ),
        migrations.AlterField(
            model_name='filmpersonmapping',
            name='department',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='media.Department'),
        ),
    ]
