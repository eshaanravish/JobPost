# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-09 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0027_auto_20170309_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
    ]