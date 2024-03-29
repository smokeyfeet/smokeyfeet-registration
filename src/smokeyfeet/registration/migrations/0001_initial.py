# Generated by Django 4.1 on 2022-09-04 09:03

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LunchType",
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
                ("name", models.CharField(max_length=64)),
                ("sort_order", models.PositiveIntegerField()),
                (
                    "unit_price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="PassType",
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
                (
                    "type",
                    models.CharField(
                        choices=[("party", "Party Pass"), ("full", "Full Pass")],
                        max_length=32,
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("active", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField()),
                ("quantity_in_stock", models.PositiveIntegerField(default=0)),
                (
                    "unit_price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                ("data", models.JSONField(blank=True)),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Registration",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("first_name", models.CharField(max_length=64)),
                ("last_name", models.CharField(max_length=64)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "dance_role",
                    models.CharField(
                        choices=[("leader", "Leader"), ("follower", "Follower")],
                        default="leader",
                        max_length=32,
                    ),
                ),
                (
                    "residing_country",
                    django_countries.fields.CountryField(max_length=2),
                ),
                ("workshop_partner_name", models.CharField(blank=True, max_length=128)),
                (
                    "workshop_partner_email",
                    models.EmailField(blank=True, max_length=254),
                ),
                ("crew_remarks", models.TextField(blank=True, max_length=4096)),
                (
                    "total_price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                ("audition_url", models.URLField(blank=True)),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "lunch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="registration.lunchtype",
                    ),
                ),
                (
                    "pass_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="registration.passtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
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
                (
                    "mollie_payment_id",
                    models.CharField(blank=True, max_length=64, null=True, unique=True),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "registration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="registration.registration",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Interaction",
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
                ("description", models.TextField(blank=True, max_length=4096)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "registration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="registration.registration",
                    ),
                ),
            ],
        ),
    ]
