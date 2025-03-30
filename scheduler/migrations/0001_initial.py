# Generated by Django 5.1.7 on 2025-03-29 01:10

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(default="Unknown Job", max_length=100)),
                ("duration_hours", models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_name", models.CharField(max_length=100)),
                ("vehicle_make", models.CharField(max_length=50)),
                ("vehicle_model", models.CharField(max_length=50)),
                ("vehicle_year", models.IntegerField()),
                ("phone_number", models.CharField(max_length=15)),
                ("custom_job", models.CharField(blank=True, max_length=100, null=True)),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("duration_hours", models.IntegerField(default=1)),
                (
                    "bay",
                    models.PositiveIntegerField(
                        choices=[(1, "Bay 1"), (2, "Bay 2"), (3, "Bay 3"), (4, "Bay 4")]
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "job",
                    models.ForeignKey(
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="scheduler.job",
                    ),
                ),
            ],
        ),
    ]
