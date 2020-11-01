# Generated by Django 2.2.5 on 2020-11-01 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceld', 'Canceld')], default='pending', max_length=12)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
