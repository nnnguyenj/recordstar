# Generated by Django 4.2.20 on 2025-04-29 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_merge_20250428_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='cover_image',
            field=models.ImageField(blank=True, default='collection_covers/default.jpg', null=True, upload_to='collection_covers/'),
        ),
    ]
