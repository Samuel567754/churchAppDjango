# Generated by Django 5.1.6 on 2025-02-19 12:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('membership', '0003_ministry_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto (System Default)')], default='light', help_text='Dashboard theme preference.', max_length=10)),
                ('receive_announcements', models.BooleanField(default=True, help_text='Receive church announcements?')),
                ('receive_notifications', models.BooleanField(default=True, help_text='Receive church notifications?')),
                ('receive_newsletters', models.BooleanField(default=True, help_text='Receive newsletters?')),
                ('receive_event_reminders', models.BooleanField(default=True, help_text='Receive event reminders?')),
                ('receive_meeting_reminders', models.BooleanField(default=True, help_text='Receive reminders for church meetings?')),
                ('show_recent_activities', models.BooleanField(default=True, help_text='Show recent activities on dashboard?')),
                ('show_service_attendance', models.BooleanField(default=True, help_text='Show personal service attendance stats?')),
                ('show_family_section', models.BooleanField(default=True, help_text='Show family section in dashboard?')),
                ('profile_visibility', models.BooleanField(default=True, help_text='Make profile visible to other church members?')),
                ('language_preference', models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish')], default='en', help_text='Preferred language for the dashboard.', max_length=5)),
                ('enable_2fa', models.BooleanField(default=False, help_text='Enable two-factor authentication for login security?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_settings', to='membership.member')),
            ],
            options={
                'verbose_name_plural': 'Memeber Settings',
            },
        ),
    ]
