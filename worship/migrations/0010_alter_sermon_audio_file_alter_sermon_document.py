# Generated by Django 5.1.6 on 2025-03-12 13:18

import worship.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0009_sermon_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sermon',
            name='audio_file',
            field=models.FileField(blank=True, help_text='Optional audio file of the sermon', null=True, upload_to='sermons/audio/', validators=[worship.models.validate_audio_file, worship.models.validate_file_size]),
        ),
        migrations.AlterField(
            model_name='sermon',
            name='document',
            field=models.FileField(blank=True, help_text='Optional document file (PDF, notes, etc.)', null=True, upload_to='sermons/documents/', validators=[worship.models.validate_document_file, worship.models.validate_file_size]),
        ),
    ]
