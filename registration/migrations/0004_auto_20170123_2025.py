# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-23 19:25
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_registration_audition_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passtype',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True),
        ),
    ]