# Generated by Django 3.0.7 on 2021-09-15 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('araincdb', '0032_multiplefileuplaoder'),
    ]

    operations = [
        migrations.CreateModel(
            name='hashtag_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.CharField(max_length=200, verbose_name='Hashtag')),
            ],
            options={
                'verbose_name': 'Hashtag List',
                'verbose_name_plural': 'Hashtags List',
            },
        ),
    ]
