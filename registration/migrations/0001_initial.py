# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-10 20:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PassType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('party', 'Party Pass'), ('full', 'Full Pass')], max_length=32)),
                ('name', models.CharField(max_length=64)),
                ('sort_order', models.PositiveIntegerField()),
                ('quantity_in_stock', models.PositiveIntegerField(default=0)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('dance_role', models.CharField(choices=[('leader', 'Leader'), ('follower', 'Follower')], default='leader', max_length=32)),
                ('residing_country', django_countries.fields.CountryField(max_length=2)),
                ('workshop_partner_name', models.CharField(blank=True, max_length=128)),
                ('workshop_partner_email', models.EmailField(blank=True, max_length=254)),
                ('include_lunch', models.BooleanField(default=False)),
                ('crew_remarks', models.TextField(blank=True, max_length=4096)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pass_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.PassType')),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('queued', 'Queued'), ('accepted', 'Accepted'), ('paid', 'Paid')], max_length=32)),
                ('status_at', models.DateTimeField(auto_now_add=True)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='registration.Registration')),
            ],
        ),
    ]
