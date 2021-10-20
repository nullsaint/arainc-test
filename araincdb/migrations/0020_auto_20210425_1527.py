# Generated by Django 3.0.7 on 2021-04-25 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('araincdb', '0019_auto_20210425_0958'),
    ]

    operations = [
        migrations.AddField(
            model_name='growth',
            name='scrapped_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Scrapped By'),
        ),
        migrations.AddField(
            model_name='growth',
            name='scrapped_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Scrapped Date'),
        ),
    ]