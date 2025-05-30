# Generated by Django 5.1.6 on 2025-03-16 20:24

import settings.fields
import worship.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0011_sermon_ppoi_alter_sermon_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sermon',
            name='ppoi',
        ),
        migrations.AlterField(
            model_name='livestream',
            name='thumbnail',
            field=settings.fields.CompressedImageField(help_text='Thumbnail for the live stream', upload_to='livestreams/'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='file',
            field=models.FileField(help_text='Upload the resource file', upload_to='resources/', validators=[worship.models.validate_document_file, worship.models.validate_file_size]),
        ),
        migrations.AlterField(
            model_name='sermon',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.AlterField(
            model_name='sermonseries',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, help_text='Optional image for the series', null=True, upload_to='sermon_series/'),
        ),
    ]
