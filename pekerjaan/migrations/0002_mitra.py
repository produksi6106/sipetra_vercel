# Generated by Django 5.2.3 on 2025-06-24 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pekerjaan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mitra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=100)),
                ('alamat', models.TextField()),
                ('no_hp', models.CharField(max_length=20)),
                ('sobat_id', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
