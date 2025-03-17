from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from worship.models import Appointment

class Command(BaseCommand):
    help = 'Archive past week’s appointments'

    def handle(self, *args, **kwargs):
        today = now().date()
        past_appointments = Appointment.objects.filter(date__lt=today, is_archived=False)

        if past_appointments.exists():
            past_appointments.update(is_archived=True)
            self.stdout.write(self.style.SUCCESS(f'Successfully archived {past_appointments.count()} appointments.'))
