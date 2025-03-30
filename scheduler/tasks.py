from datetime import datetime, timedelta
from .models import Appointment

def cleanup_old_appointments():
    threshold_date = datetime.today().date() - timedelta(days=60)
    Appointment.objects.filter(date__lt=threshold_date).delete()
