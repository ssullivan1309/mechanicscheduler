from django.db import models
from django.utils.timezone import now
from datetime import datetime, timedelta

class Job(models.Model):
    title = models.CharField(max_length=100, default="Unknown Job")
    duration_hours = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.title

class Appointment(models.Model):
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    vehicle_make = models.CharField(max_length=50, blank=True, null=True)
    vehicle_model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_year = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Use Many-to-Many for jobs
    jobs = models.ManyToManyField(Job, blank=True)
    
    # For custom job if required
    #custom_job = models.CharField(max_length=100, blank=True, null=True)
    custom_job_name = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.DateTimeField(default=now)
    duration_hours = models.IntegerField(default=1)  # Total duration for the appointment
    bay = models.PositiveIntegerField(choices=[(i, f"Bay {i}") for i in range(1, 5)])
    notes = models.TextField(blank=True, null=True)

    @property
    def end_time(self):
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        # Calculate total duration for the appointment from all jobs
        total_duration = sum(job.duration_hours for job in self.jobs.all())
        end_datetime = start_datetime + timedelta(hours=total_duration)
        return end_datetime.time()

    
    #def __str__(self):
        #return f"{self.customer_name} - {self.job.name}"