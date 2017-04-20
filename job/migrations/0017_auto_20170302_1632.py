# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-02 11:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0016_auto_20170302_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('email', models.EmailField(max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='job.Job')),
            ],
        ),
        migrations.AddField(
            model_name='applicant',
            name='resume',
            field=models.FileField(null=True, upload_to='docs/'),
        ),
        migrations.AddField(
            model_name='employee',
            name='applicant_pic',
            field=models.ImageField(default='images/None/no-img.jpg', upload_to='images/'),
        ),
    ]