from django.contrib import admin
from .models import Job, Applicant, Employee, ApplicationTime, Messages, UsersMessage, MailedContent



class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'created_by', 'job_location', 'job_availability')

admin.site.register(Job, JobAdmin)

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('username', 'dob', 'skills')

admin.site.register(Applicant, ApplicantAdmin)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'email', 'joining_date')

admin.site.register(Employee, EmployeeAdmin)

class ApplicationTimeAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'applied_at', 'telephonic_call_at', 'technical_round_call_at', 'hr_round_call_at', 'selection_call_at', 'declined_at')

admin.site.register(ApplicationTime, ApplicationTimeAdmin)


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'job_message')

admin.site.register(Messages, MessagesAdmin)


class UsersMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'job')

admin.site.register(UsersMessage, UsersMessageAdmin)


class MailedContentAdmin(admin.ModelAdmin):
    list_display = ('status_mailed_for', 'application_time', 'mailed_content')

admin.site.register(MailedContent, MailedContentAdmin)
