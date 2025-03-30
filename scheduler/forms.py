from django import forms
from .models import Appointment, Job

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['customer_name', 'phone_number', 'vehicle_make', 'vehicle_model', 'vehicle_year', 
                  'bay', 'job', 'custom_job', 'start_time', 'duration', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.NumberInput(attrs={'type': 'number', 'min': 1}),
        }
