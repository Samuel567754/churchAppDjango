# Generated by Django 5.1.6 on 2025-03-16 20:24

import settings.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselitem',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, null=True, upload_to='carousel_images/'),
        ),
    ]
