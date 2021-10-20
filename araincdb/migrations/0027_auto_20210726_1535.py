# Generated by Django 3.0.7 on 2021-07-26 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('araincdb', '0026_auto_20210630_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='growthdedupe',
            name='caption',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Caption'),
        ),
        migrations.AddField(
            model_name='growthdedupe',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Full Name'),
        ),
        migrations.AddField(
            model_name='growthdedupe',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='growthunique',
            name='caption',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Caption'),
        ),
        migrations.AddField(
            model_name='growthunique',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Full Name'),
        ),
        migrations.AddField(
            model_name='growthunique',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Location'),
        ),
        migrations.CreateModel(
            name='Listingunique',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_username', models.CharField(max_length=200, verbose_name='Username')),
                ('full_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Full Name')),
                ('hashtag', models.CharField(blank=True, max_length=200, null=True, verbose_name='Hashtag')),
                ('client_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='araincdb.Client', verbose_name='Client Name')),
            ],
            options={
                'verbose_name': 'Listingunique',
                'verbose_name_plural': 'Listingunique',
            },
        ),
        migrations.CreateModel(
            name='Listingdedupe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_username', models.CharField(max_length=200, verbose_name='Username')),
                ('full_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Full Name')),
                ('hashtag', models.CharField(blank=True, max_length=200, null=True, verbose_name='Hashtag')),
                ('client_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='araincdb.Client', verbose_name='Client Name')),
            ],
            options={
                'verbose_name': 'Listingdedupe',
                'verbose_name_plural': 'Listingdedupe',
            },
        ),
    ]