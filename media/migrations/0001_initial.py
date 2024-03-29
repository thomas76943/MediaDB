# Generated by Django 3.0.3 on 2020-04-14 16:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoBookTitleSpecified', max_length=500)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('imageFilePath', models.CharField(default='NoFilePathSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='NoFilmStudioNameSpecified', max_length=500)),
                ('baseCountry', models.CharField(default='NoCountrySpecified', max_length=500)),
                ('dateFounded', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('companyRoleName', models.CharField(default='NoCompanyRoleNameSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoFilmTitleSpecified', max_length=500)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('posterFilePath', models.CharField(default='NoFilePathSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Franchise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoFranchiseNameSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoFilmGenreSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(default='NoFirstNameSpecified', max_length=500)),
                ('surname', models.CharField(default='NoSurnameSpecified', max_length=500)),
                ('DoB', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='PersonRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='NoRoleNameSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Television',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoTelevisionTitleSpecified', max_length=500)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('posterFilePath', models.CharField(default='NoFilePathSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='VideoGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoVideoGameTitleSpecified', max_length=500)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('posterFilePath', models.CharField(default='NoFilePathSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='VideoGameGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoVideoGameGenreSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='WebSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='NoWebSeriesTitleSpecified', max_length=500)),
                ('release', models.DateField(default=django.utils.timezone.now)),
                ('posterFilePath', models.CharField(default='NoFilePathSpecified', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='WebSeriesPersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.PersonRole')),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
        ),
        migrations.CreateModel(
            name='WebSeriesGenreMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Genre')),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
        ),
        migrations.CreateModel(
            name='WebSeriesFranchiseMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Franchise')),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
        ),
        migrations.CreateModel(
            name='WebSeriesCompanyMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Company')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.CompanyRole')),
                ('webSeries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.WebSeries')),
            ],
        ),
        migrations.CreateModel(
            name='VideoGamePersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.PersonRole')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
        ),
        migrations.CreateModel(
            name='VideoGameGenreMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGameGenre')),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
        ),
        migrations.CreateModel(
            name='VideoGameFranchiseMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Franchise')),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
        ),
        migrations.CreateModel(
            name='VideoGameCompanyMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Company')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.CompanyRole')),
                ('videoGame', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.VideoGame')),
            ],
        ),
        migrations.CreateModel(
            name='TelevisionPersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.PersonRole')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
            ],
        ),
        migrations.CreateModel(
            name='TelevisionGenreMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Genre')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
            ],
        ),
        migrations.CreateModel(
            name='TelevisionFranchiseMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Franchise')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
            ],
        ),
        migrations.CreateModel(
            name='TelevisionCompanyMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Company')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.CompanyRole')),
                ('television', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Television')),
            ],
        ),
        migrations.CreateModel(
            name='FilmPersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.PersonRole')),
            ],
        ),
        migrations.CreateModel(
            name='FilmGenreMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Genre')),
            ],
        ),
        migrations.CreateModel(
            name='FilmFranchiseMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Franchise')),
            ],
        ),
        migrations.CreateModel(
            name='FilmCompanyMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Company')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Film')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.CompanyRole')),
            ],
        ),
        migrations.CreateModel(
            name='BookPersonMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Person')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.PersonRole')),
            ],
        ),
        migrations.CreateModel(
            name='BookGenreMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Genre')),
            ],
        ),
        migrations.CreateModel(
            name='BookFranchiseMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Franchise')),
            ],
        ),
        migrations.CreateModel(
            name='BookCompanyMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Book')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.Company')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='media.CompanyRole')),
            ],
        ),
    ]
