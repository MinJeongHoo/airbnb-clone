# Generated by Django 2.2.5 on 2020-11-03 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='check_in',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='review',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='rooms.Room'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL),
        ),
    ]