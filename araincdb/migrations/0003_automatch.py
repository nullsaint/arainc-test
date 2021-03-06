# Generated by Django 3.0.7 on 2021-02-25 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('araincdb', '0002_tempgrowth_client_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Automatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=200, verbose_name='Keyword')),
                ('client_name', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='araincdb.Client', verbose_name='Client Name')),
            ],
            options={
                'verbose_name': 'Automatch',
                'verbose_name_plural': 'Automatches',
            },
        ),
    ]
