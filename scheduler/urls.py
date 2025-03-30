from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_schedule, name='daily_schedule'),
    path('schedule/<str:date>/', views.daily_schedule, name='daily_schedule_date'),
    path('add/', views.add_appointment, name='add_appointment'),
    path('delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path("search/", views.search_appointments, name="search_appointments"),
]


