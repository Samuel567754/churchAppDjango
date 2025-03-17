# Generated by Django 5.1.6 on 2025-03-12 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0008_serviceattendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='sermon',
            name='document',
            field=models.FileField(blank=True, help_text='Optional document file (PDF, notes, etc.)', null=True, upload_to='sermons/documents/'),
        ),
    ]
