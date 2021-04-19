# Generated by Django 3.0.3 on 2021-04-14 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0138_auto_20210414_1032'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoBookSpecified', max_length=500)),
                ('image', models.ImageField(blank=True, default='', upload_to='icons')),
                ('slug', models.SlugField(blank=True, default='', max_length=150)),
            ],
            options={
                'verbose_name': 'Genre - Book',
                'verbose_name_plural': 'Genres - Books',
            },
        ),
    ]