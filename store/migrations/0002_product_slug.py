# Generated by Django 4.1.4 on 2022-12-07 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(null=True, unique=True),
        ),
    ]
