# Generated by Django 5.1.3 on 2025-02-06 05:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Church',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='church_logos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_churches', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_churches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Churches',
            },
        ),
    ]
