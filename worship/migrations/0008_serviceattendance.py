# Generated by Django 5.1.6 on 2025-02-17 08:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0007_appointment_is_archived'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('day', models.CharField(choices=[('Sunday', 'Sunday'), ('Tuesday', 'Tuesday'), ('Friday', 'Friday')], max_length=10)),
                ('total_attendance', models.PositiveIntegerField(default=0)),
                ('males', models.PositiveIntegerField(default=0)),
                ('females', models.PositiveIntegerField(default=0)),
                ('adults', models.PositiveIntegerField(default=0)),
                ('children', models.PositiveIntegerField(default=0)),
                ('visitors', models.PositiveIntegerField(default=0)),
                ('absent_informed', models.PositiveIntegerField(default=0)),
                ('absent_not_informed', models.PositiveIntegerField(default=0)),
                ('students_absent', models.PositiveIntegerField(default=0)),
                ('traveled', models.PositiveIntegerField(default=0)),
                ('sick', models.PositiveIntegerField(default=0)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'unique_together': {('date', 'day')},
            },
        ),
    ]
