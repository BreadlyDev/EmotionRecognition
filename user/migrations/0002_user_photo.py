# Generated by Django 5.1.2 on 2024-12-22 06:34

import user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(null=True, upload_to=user.models.user_photo_path),
        ),
    ]
