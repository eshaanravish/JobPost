from __future__ import unicode_literals
import zlib

from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget

from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils import timezone
from django.core.files import File
import datetime


class Job(models.Model):

    JOB_LOCATION_CHOICES = (
        ('delhi','DELHI'),
        ('noida', 'NOIDA'),
        ('gurgaon','GURGAON'),
        ('banglore','BANGLORE'),
        ('pune','PUNE'),
    )
    JOB_EXPERIENCE_YEARS = (
        ('0','0'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12','12'),
        ('13','13'),
        ('14','14'),
        ('15','15'),
        ('16','16'),
        ('17','17'),
        ('18','18'),
        ('19','19'),
        ('20','20'),
    )
    JOB_EXPERIENCE_MONTHS = (
        ('0','0'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ('11','11'),
        ('12','12'),
    )

    job_title = models.CharField(max_length=50)
    job_description = RichTextField(max_length=1255)
    job_location = models.CharField(max_length=20, choices = JOB_LOCATION_CHOICES)
    job_skillsrequired = models.CharField(max_length=100)
    job_minqualification = models.CharField(max_length=100, blank=True, null=True)
    job_experience = models.CharField(max_length=1, blank=True, null=True, default='0', choices = JOB_EXPERIENCE_YEARS)
    job_experience_months = models.CharField(max_length=2, blank=True, null=True, default='0', choices = JOB_EXPERIENCE_MONTHS)
    created_by = models.ForeignKey(User, blank=True, null=True)
    applied_by = models.ManyToManyField(User, related_name= 'Applicant', blank=True)
    likes = models.ManyToManyField(User, related_name = 'likes', blank=True)
    job_posted_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    job_valid_upto = models.DateField(blank=True, null=True)
    job_availability = models.BooleanField(default=True)

    def __str__(self):
        return self.job_title

    def get_year(self):
        return dict(self.JOB_EXPERIENCE_YEARS).get(self.job_experience)

    def get_month(self):
        return dict(self.JOB_EXPERIENCE_MONTHS).get(self.job_experience_months)

class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    employee = models.ForeignKey(User, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, default=0,  choices = GENDER_CHOICES)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=100)
    contact = models.CharField(max_length=10)
    dob = models.DateField(blank=True, null=True)
    joining_date = models.DateTimeField('Joining Date',blank=True, null=True)
    employee_pic = models.ImageField(upload_to = 'media/', default = 'media/None/no-img.jpg')


    def __str__(self):
        return self.first_name

    def get_gender(self):
        return dict(self.GENDER_CHOICES).get(self.gender)


class Applicant(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    applicant_pic = models.ImageField(upload_to = 'media/', default = '/None/no-img.jpg')
    username = models.ForeignKey(User, blank=True, null=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    applicant_gender = models.CharField(max_length=1, default='M', choices = GENDER_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    tenth_percentage = models.FloatField(blank=True, null=True)
    twelth_percentage = models.FloatField(blank=True, null=True)
    graduation = models.CharField(max_length=255, blank=True, null=True)
    graduation_percentage = models.FloatField(blank=True, null=True)
    post_graduation = models.CharField(max_length=255, blank=True, null=True)
    post_graduation_percentage = models.FloatField(blank=True, null=True)
    currently_working_with = models.CharField(max_length=255, blank=True, null=True)
    current_position = models.CharField(max_length=255, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    skills = models.CharField(max_length=30, blank=True, null=True)
    resume = models.FileField(upload_to = 'docs/', blank=True, null=True)


    def gender(self):
        return dict(self.GENDER_CHOICES).get(self.applicant_gender)

    def __str__(self):
        return str(self.username)


class ApplicationTime(models.Model):
    APPLICANT_STATUS= (
        ('1', 'Applied'),
        ('2', 'Called for Telephonic round'),
        ('3', 'Called for Technical round'),
        ('4', 'Called for HR round'),
        ('5', 'Selected'),
        ('6', 'Declined')
    )
    applicant = models.ForeignKey(User, blank=True, null=True)
    job = models.ForeignKey(Job, blank=True, null=True)
    applicant_status = models.CharField(max_length=255, default='1', choices = APPLICANT_STATUS)
    applied_at = models.DateTimeField('Applied At')
    telephonic_call_at = models.DateTimeField(blank=True, null=True)
    technical_round_call_at = models.DateTimeField(blank=True, null=True)
    hr_round_call_at = models.DateTimeField(blank=True, null=True)
    selection_call_at = models.DateTimeField(blank=True, null=True)
    declined_at = models.DateTimeField(blank=True, null=True)

    def get_status(self):
        return dict(self.APPLICANT_STATUS).get(self.applicant_status)

    def __str__(self):
        return self.applicant_status

class MailedContent(models.Model):
    STATUS_MAILED_FOR= (
        ('1', 'Applied'),
        ('2', 'Called for Telephonic round'),
        ('3', 'Called for Technical round'),
        ('4', 'Called for HR round'),
        ('5', 'Selected'),
    )
    application_time = models.ForeignKey(ApplicationTime)
    status_mailed_for = models.CharField(max_length=255, default='1', choices = STATUS_MAILED_FOR)
    mailed_content = models.CharField(max_length=5000, default='')

    def get_status(self):
        return dict(self.STATUS_MAILED_FOR).get(self.status_mailed_for)

    def __int__(self):
        return self.status_mailed_for

class Messages(models.Model):
    job_message = models.ForeignKey(Job, related_name='comments')
    name = models.CharField(max_length=50)
    email = models.EmailField()
    body = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UsersMessage(models.Model):
    job = models.ForeignKey(Job, related_name='UserMessage', blank=True, null=True)
    name = models.ForeignKey(User, blank=True, null=True)
    body = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.name
