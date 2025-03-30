from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now, make_aware, is_naive
from datetime import datetime, timedelta
from .models import Appointment, Job
import json
from django.http import JsonResponse
from .models import Appointment

def daily_schedule(request, date=None):
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = now().date()
    else:
        selected_date = now().date()

    day_of_week = selected_date.strftime('%A')
    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    today_date = now().date()

    time_slots = [datetime.strptime(f'{hour}:00', "%H:%M").strftime('%I:%M %p') for hour in range(8, 17)]
    appointments = Appointment.objects.filter(start_time__date=selected_date)

    # Build a map of appointment by (time_label, bay)
    slot_map = {}
    skip_tracker = set()

    for appointment in appointments:
        start_hour = appointment.start_time.replace(minute=0)
        time_label = start_hour.strftime('%I:%M %p')
        key = (time_label, appointment.bay)
        slot_map[key] = appointment

        # Mark future hours as SKIP
        for i in range(1, int(appointment.duration_hours)):
            future_time = start_hour + timedelta(hours=i)
            future_label = future_time.strftime('%I:%M %p')
            skip_tracker.add((future_label, appointment.bay))

    # Build the final schedule to render
    render_schedule = []
    for time in time_slots:
        row = []
        for bay in range(1, 5):
            key = (time, bay)
            if key in skip_tracker:
                row.append("SKIP")
            else:
                row.append(slot_map.get(key))
        render_schedule.append((time, row))

    context = {
        "selected_date": selected_date,
        "day_of_week": day_of_week,
        "previous_date": previous_date,
        "next_date": next_date,
        "today_date": today_date,
        "schedule": render_schedule,
        "appointments": appointments,
    }

    return render(request, "scheduler/daily_schedule.html", context)
def calendar_view(request):
    selected_date = request.GET.get("date", now().date())
    return render(request, "scheduler/calendar_view.html", {"selected_date": selected_date})


def add_appointment(request):
    today_date = now().date()
    three_months_ahead = today_date + timedelta(weeks=12)

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "")
        vehicle_make = request.POST.get("vehicle_make", "")
        vehicle_model = request.POST.get("vehicle_model", "")
        vehicle_year = request.POST.get("vehicle_year", None)
        phone_number = request.POST.get("phone_number", "")
        job_ids = request.POST.getlist("jobs[]")
        durations = request.POST.getlist("durations[]")
        custom_job_names = request.POST.getlist("custom_job_name[]")
        custom_durations = request.POST.getlist("custom_duration[]")
        start_time = request.POST.get("start_time")
        bay = int(request.POST.get("bay"))
        notes = request.POST.get("notes") or None
        date = request.POST.get("date")

        if not job_ids or not start_time or not bay or not date:
            return render(request, 'scheduler/add_appointment.html', {
                'error': 'Job, time, date, and bay are required fields.',
                'jobs': Job.objects.all()
            })

        appointment_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
        if is_naive(appointment_datetime):
            appointment_datetime = make_aware(appointment_datetime)

        if appointment_datetime.weekday() >= 5:
            return render(request, 'scheduler/add_appointment.html', {
                'error': 'Appointments can only be booked on weekdays (Monday to Friday).',
                'jobs': Job.objects.all()
            })

        appointment = Appointment(
            customer_name=customer_name or None,
            vehicle_make=vehicle_make or None,
            vehicle_model=vehicle_model or None,
            vehicle_year=vehicle_year if vehicle_year else None,
            phone_number=phone_number or None,
            start_time=appointment_datetime,
            bay=bay,
            duration_hours=0,
            notes=notes or None
        )
        appointment.save()

        for job_id, duration in zip(job_ids, durations):
            if job_id == "custom":
                custom_job_name = custom_job_names.pop(0)
                custom_duration = float(custom_durations.pop(0))
                appointment.custom_job_name = custom_job_name
                appointment.duration_hours += custom_duration
            else:
                job = Job.objects.get(id=job_id)
                appointment.jobs.add(job)
                appointment.duration_hours += float(duration)

        end_datetime = appointment.start_time + timedelta(hours=appointment.duration_hours)

        if appointment.start_time.hour < 8 or end_datetime > appointment.start_time.replace(hour=17, minute=0):
            appointment.delete()
            return render(request, 'scheduler/add_appointment.html', {
                'error': 'Appointments must start at or after 8:00 AM and end by 5:00 PM.',
                'jobs': Job.objects.all()
            })

        overlapping = Appointment.objects.filter(
            start_time__date=appointment_datetime.date(),
            bay=bay
        ).exclude(id=appointment.id)

        for existing in overlapping:
            existing_start = existing.start_time
            existing_end = existing_start + timedelta(hours=existing.duration_hours)

            if is_naive(existing_start):
                existing_start = make_aware(existing_start)
            if is_naive(existing_end):
                existing_end = make_aware(existing_end)

            if existing_start < end_datetime and appointment.start_time < existing_end:
                appointment.delete()
                return render(request, 'scheduler/add_appointment.html', {
                    'error': 'This bay already has an appointment during the selected time. Please choose another time or bay.',
                    'jobs': Job.objects.all()
                })

        appointment.save()
        return redirect('daily_schedule')

    jobs = Job.objects.all()
    return render(request, 'scheduler/add_appointment.html', {"jobs": jobs})


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect('daily_schedule')

def edit_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        appointment.custom_job_name = data.get("job", "") or None
        appointment.customer_name = data.get("customer", "") or None
        appointment.vehicle_year = data.get("year") or None
        appointment.vehicle_make = data.get("make", "") or None
        appointment.vehicle_model = data.get("model", "") or None
        appointment.phone_number = data.get("phone", "") or None
        appointment.notes = data.get("notes", "") or None

        appointment.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def search_appointments(request):
    upcoming_appointments = []
    previous_appointments = []

    if request.method == "GET" and any(param in request.GET for param in ["name", "date", "time", "phone", "vehicle_make", "vehicle_model", "vehicle_year"]):
        name = request.GET.get("name")
        date = request.GET.get("date")
        time = request.GET.get("time")
        phone = request.GET.get("phone")
        vehicle_make = request.GET.get("vehicle_make")
        vehicle_model = request.GET.get("vehicle_model")
        vehicle_year = request.GET.get("vehicle_year")

        filters = {}
        if name:
            filters["customer_name__icontains"] = name
        if phone:
            filters["phone_number__icontains"] = phone
        if vehicle_make:
            filters["vehicle_make__icontains"] = vehicle_make
        if vehicle_model:
            filters["vehicle_model__icontains"] = vehicle_model
        if vehicle_year:
            filters["vehicle_year__icontains"] = vehicle_year
        if date:
            filters["start_time__date"] = date
        if time and date:
            filters["start_time__time"] = time

        all_results = Appointment.objects.filter(**filters)

        for appt in all_results:
            if appt.start_time >= now():
                upcoming_appointments.append(appt)
            else:
                previous_appointments.append(appt)

    return render(request, "scheduler/search_appointments.html", {
        "upcoming_appointments": upcoming_appointments,
        "previous_appointments": previous_appointments
    })