# Generated by Django 2.2.5 on 2020-11-05 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20201103_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_confirm',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='currency',
            field=models.CharField(blank=True, choices=[('usd', 'USD'), ('kor', 'KOR')], default='kor', max_length=3),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, choices=[('english', 'English'), ('korean', 'Korean')], default='korean', max_length=2),
        ),
    ]
