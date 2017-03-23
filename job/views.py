import json
import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect

from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset as django_password_reset
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import RequestContext
from django.template import Context

from django.core.mail import EmailMessage
from django.core.mail import send_mail, mail_admins
from django.template import Context
from django.template.loader import get_template

from django.contrib.auth.models import User
from job.models import Job, Employee, Applicant, ApplicationTime, Messages, UsersMessage, MailedContent

from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from django import forms
from job.forms import UserForm, CreateJob, EmployeeForm, ApplicantForm, MessagesForm, MailtoApplicantForm, UsersMessageForm, SearchForm
import operator

from django.db.models import Q


def homepage(request):
    q = request.GET.get('q', '')
    jobs = Job.objects.filter()
    employees = Employee.objects.all()

    if q:
        jobs = jobs.filter(Q(job_title__icontains=q) | Q(job_description__icontains=q) | Q(job_skillsrequired__icontains=q) | Q(job_location__icontains=q))

    return render(request, 'job/homepage.html', {'jobs':jobs, 'employees': employees})

def recruiterrespectivejobs(request, user_id):
    job = Job.objects.filter(created_by__id = user_id)
    user = User.objects.get(pk= user_id)
    user_comments = Messages.objects.filter(job_message__in = job)
    return render(request, 'job/recruiter_respective_jobs.html', {'job':job, 'user': user, 'user_comments': user_comments})

def location(request, job_location):
    jobs = Job.objects.filter(job_location = job_location)
    return render(request, 'job/location_specific_jobs.html', {'jobs':jobs})

def applicantsignup(request):
    if request.method == "POST":
        form = UserForm(request.POST, use_required_attribute=False)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            user.save()
            login(request, user)
            applier = Applicant.objects.create()
            applier.username = request.user
            applier.save()
            return redirect('/login/',
                messages.add_message(request, messages.SUCCESS, 'Registered Successfully, Now you can Login.')
            )
        else:
            error_message = "Please fill the valid details."
            return render(request, 'job/signup_form.html', {'form': form, 'error_message': error_message})
    else:
        error_message = ""
        form = UserForm(use_required_attribute=False)
    return render(request, 'job/signup_form.html', {'form': form, 'error_message': error_message})

@login_required(login_url="login/")
def applicantprofile(request, user_id):
    users = Applicant.objects.get(username__id=user_id)
    user = User.objects.get(pk=user_id)
    return render(request, 'job/applicantprofile.html', {'user': user, 'users':users})

@login_required(login_url="login/")
def employeeprofile(request, user_id):
    employee = Employee.objects.get(employee__id=user_id)
    user = User.objects.get(pk=user_id)
    return render(request, 'job/employeeprofile.html',{'user': request.user, 'employee': employee})

@login_required(login_url="login/")
def editemployeeprofile(request, user_id):
    employee = Employee.objects.get(employee__id = user_id)
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, instance=employee, use_required_attribute=False)
        if form.is_valid():
            print form.cleaned_data
            user = User.objects.get(pk=user_id)
            e = form.save(commit= False)
            e.save()
            f = Employee(employee_pic=request.FILES['employee_pic'])
            f.save()
            return redirect(reverse('employeepage', args=[user.id]),
            messages.success(request, 'Profile details updated.')
            )
        else:
            error_message = "Please fill the valid details."
            return render(request, 'job/editemployee.html', {'form': form, 'error_message': error_message, 'employee': employee})
    else:
        error_message = ""
        form = EmployeeForm(instance = employee, use_required_attribute=False)
    return render(request, 'job/editemployee.html', {'form': form, 'error_message': error_message, 'employee': employee})

@login_required(login_url="login/")
def editapplicantprofile(request, user_id):
    applicant = Applicant.objects.get(username__id = user_id)
    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES, instance=applicant, use_required_attribute=False)
        if form.is_valid():
            print form.cleaned_data
            user = User.objects.get(pk=user_id)
            a = form.save(commit= False)
            a.save()
            b = Applicant(applicant_pic=request.FILES['applicant_pic'])
            b.save()
            return redirect(reverse('applicantpage', args=[user.id]),
            messages.success(request, 'Profile details updated.')
            )
        else:
            print form.errors
            error_message = "Please fill the valid details."
            return render(request, 'job/editapplicant.html', {'form': form, 'error_message': error_message, 'applicant': applicant})
    else:
        error_message = ""
        form = ApplicantForm(instance = applicant, use_required_attribute=False)
    return render(request, 'job/editapplicant.html', {'form': form, 'error_message': error_message, 'applicant': applicant})

def applicantlogin(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect(reverse('employeepage', args=[user.id]))
                    pass
                else:
                    return redirect(reverse('applicantpage', args=[user.id]))
                    pass
            else:
                error_message = "You have provided invalid credentials."
        else:
            error_message = "All fields are mandatory."
    else:
        error_message = ""
    return render(request, 'job/login.html', {'error_message': error_message})

@login_required(login_url="login/")
def employeepage(request, user_id):
    users = User.objects.all()
    all_jobs = Job.objects.all()
    employee = Employee.objects.get(employee__id = user_id)
    return render(request, 'job/employee_page.html',{'user': request.user, 'users': users, 'employee': employee, 'all_jobs': all_jobs})

@login_required(login_url="login/")
def applicantpage(request, user_id):
    user = User.objects.get(pk= user_id)
    applicantjobs = Job.objects.filter(job_availability = True)
    applicant = Applicant.objects.get(username__id = user_id)
    return render(request, 'job/applicant_page.html', {'applicant': applicant, 'user': request.user, 'user': user, 'applicantjobs': applicantjobs})

@login_required(login_url="login/")
def alljobs(request, user_id):
    user = User.objects.get(pk= user_id)
    all_jobs = Job.objects.all()
    return render(request, 'job/all_jobs.html', {'user': request.user,'user': user, 'all_jobs': all_jobs})

@login_required(login_url="login/")
def likes(request, user_id, jobs_id):
    if request.is_ajax():
        liked_job = Job.objects.get(pk = jobs_id)
        user = User.objects.get(pk= user_id)
        liked_job.likes.add(request.user)
        response = {'status': True}
        return HttpResponse(json.dumps(response))
    else:
        Http404

@login_required(login_url="login/")
def unlikes(request, user_id, jobs_id):
    if request.is_ajax():
        unliked_job = Job.objects.get(pk = jobs_id)
        user = User.objects.get(pk= user_id)
        unliked_job.likes.remove(request.user)
        response = {'status': True}
        return HttpResponse(json.dumps(response))
    else:
        Http404

@login_required(login_url="login/")
def userlogout(request):
    logout(request)
    return redirect('/')

@login_required(login_url="login/")
def createjob(request, user_id):
    if request.method == "POST":
        user = User.objects.get(pk=user_id)
        form = CreateJob(request.POST, use_required_attribute=False)
        if form.is_valid():
            new_job = Job.objects.create(**form.cleaned_data)
            new_job.created_by = request.user
            new_job.save()
            return redirect(reverse('employeepage', args=[user.id]))
        else:
            error_message = "All fields are mandatory."
            return render(request, 'job/createjob.html', {'form': form})
    else:
        error_message = ""
        form = CreateJob(use_required_attribute=False)
    return render(request, 'job/createjob.html', {'error_message': error_message, 'form':form})

@login_required(login_url="login/")
def employeejobs(request, user_id):
    jobs = Job.objects.filter(created_by__id = user_id)
    return render(request, 'job/employeejobs.html', {'jobs':jobs})

@login_required(login_url="login/")
def deletejob(request, jobs_id, user_id):
    jobs = Job.objects.filter(created_by__id = user_id)
    delete_job = Job.objects.get(pk = jobs_id)
    delete_job.delete()
    return render(request, 'job/employeejobs.html', {'jobs':jobs})

@login_required(login_url="login/")
def applyjob(request, jobs_id):
    if request.is_ajax():
        job = Job.objects.get(pk=jobs_id)
        job.applied_by.add(request.user)
        user = request.user
        appliedat = ApplicationTime.objects.create(
            applicant = request.user,
            job = job,
            applied_at = timezone.now(),
            applicant_status = "1",
            )
        response = {'status': True}
        return HttpResponse(json.dumps(response))
    else:
        Http404

@login_required(login_url="login/")
def applicantslist(request, jobs_id):
    job = Job.objects.get(pk=jobs_id)
    messages = UsersMessage.objects.filter(job__id = jobs_id)
    application = ApplicationTime.objects.filter(job__id = jobs_id)
    return render(request, 'job/applicants_list.html', {'job':job, 'application':application, 'messages': messages})

@login_required(login_url="login/")
def details(request, user_id):
    user = Applicant.objects.get(pk= user_id)
    return render(request, 'job/details.html', {'user':user})

@login_required(login_url="login/")
def usermessage(request, user_id, jobs_id):
    user = User.objects.get(pk = user_id)
    applicant = Applicant.objects.get(username__in = [request.user])
    job = Job.objects.get(pk=jobs_id)
    if request.method == "POST":
        form = UsersMessageForm(request.POST, use_required_attribute=False)
        if form.is_valid():
            print form.cleaned_data
            new_message = UsersMessage.objects.create(**form.cleaned_data)
            new_message.name = user
            new_message.job = job
            new_message.save()
            return render(request, 'job/jobdetail.html', {'form': form, 'user': request.user,'user': user, 'job': job, 'applicant':applicant})
        else:
            error_message = "Message can't be Empty"
            return render(request, 'job/jobdetail.html', {'form': form, 'error_message': error_message, 'user': request.user,'user': user, 'job': job, 'applicant':applicant})
    else:
        error_message = ""
        form = UsersMessageForm(use_required_attribute=False)
    return render(request, 'job/jobdetail.html', {'form': form, 'job':job, 'error_message': error_message, 'user': request.user,'user': user, 'applicant':applicant})

@login_required(login_url="login/")
def userdetail(request, user_id, jobs_id, applicant_id):
    applicant = Applicant.objects.get(username__id = applicant_id)
    user = User.objects.get(pk = applicant_id)
    job = Job.objects.get(pk=jobs_id)
    job_applied = ApplicationTime.objects.get(job__id=jobs_id, applicant__id=applicant_id)
    mail_form = MailtoApplicantForm
    if request.method == "POST":
        form = mail_form(data=request.POST)
        if form.is_valid():
            # mail to applicant and revert the employee to the applicant list page.
            email = request.POST.get('email', '')
            title = request.POST.get('title', '')
            body = request.POST.get('body', '')
            template = get_template('mailtoapplicant.txt')
            context = Context({
            'email': email,
            'title': title,
            'body': body,
            })
            content = template.render(context)
            email = EmailMessage(
                title,
                content,
                "Job Post" +'',
                [ user.email ],
                headers = {'Reply-To': email }
            )
            email.send()
            job_applied = ApplicationTime.objects.get(job__id=jobs_id, applicant__id=applicant_id)
            if (title == "Call for Telephonic Interview"):
                mailed_content = MailedContent.objects.create(
                    application_time = job_applied,
                    status_mailed_for = '2',
                    mailed_content = body
                )
                mailed_content.save()
                job_applied.applicant_status = "2"
                job_applied.telephonic_call_at = timezone.now()
                job_applied.save()
            elif (title == "Call for Personal Interview"):
                mailed_content = MailedContent.objects.create(
                    application_time = job_applied,
                    status_mailed_for = '3',
                    mailed_content = body
                )
                mailed_content.save()
                job_applied.applicant_status = "3"
                job_applied.technical_round_call_at = timezone.now()
                job_applied.save()
            elif (title == "Call for HR Interview"):
                mailed_content = MailedContent.objects.create(
                    application_time = job_applied,
                    status_mailed_for = '4',
                    mailed_content = body
                )
                mailed_content.save()
                job_applied.applicant_status = "4"
                job_applied.hr_round_call_at = timezone.now()
                job_applied.save()
            elif (title == "Joining Letter"):
                mailed_content = MailedContent.objects.create(
                    application_time = job_applied,
                    status_mailed_for = '5',
                    mailed_content = body
                )
                mailed_content.save()
                job_applied.applicant_status = "5"
                job_applied.selection_call_at = timezone.now()
                job_applied.save()
                return render(request, 'job/user_details.html', {'form': form, 'applicant':applicant, 'user': user, 'job': job, 'job_applied': job_applied})
    else:
        form = mail_form(data=request.POST)
    return render(request, 'job/user_details.html', {'form': form, 'applicant':applicant, 'user': user, 'job': job, 'job_applied': job_applied})

def Mailedcontent(request, jobs_id, job_applied_id):
    job = Job.objects.get(pk = jobs_id)
    status = ApplicationTime.objects.get(pk = job_applied_id)
    return render(request, 'job/mailed_content.html', {'job':job, 'status': status})

@login_required(login_url="login/")
def appliedjobs(request, user_id):
    job = Job.objects.filter(applied_by__id = user_id)
    status = ApplicationTime.objects.filter(applicant__id = user_id, job__id = job)
    return render(request, 'job/jobs_applied.html', {'job':job, 'status': status})

@login_required(login_url="login/")
def jobstatus(request, user_id, jobs_id):
    job = Job.objects.get(pk = jobs_id)
    status = ApplicationTime.objects.get(applicant__id = user_id, job__id = jobs_id)
    return render(request, 'job/job_status.html', {'job':job, 'status': status})

def jobmessages(request, jobs_id):
    job = Job.objects.get(pk = jobs_id)
    user = Messages.objects.filter(job_message__id = jobs_id)
    if request.method == "POST":
        form = MessagesForm(request.POST, use_required_attribute=False)
        if form.is_valid():
            new_message = Messages(**form.cleaned_data)
            new_message.job_message = job
            new_message.save()
            return render(request, 'job/jobs_comments.html', {'job':job, 'user': user, 'form': form})
        else:
            error_message = "All fields required."
            return render(request, 'job/jobs_comments.html', {'job': job, 'user': user, 'form': form, 'error_message': error_message})
    else:
        error_message = ""
        form = MessagesForm(use_required_attribute=False)
    return render(request, 'job/jobs_comments.html', {'job':job, 'user': user, 'form': form})

@login_required(login_url="login/")
def rejection(request, jobs_id, user_id):
    job = Job.objects.get(pk=jobs_id)
    job_rejected = ApplicationTime.objects.get(job__id=jobs_id, applicant__id=user_id)
    job_rejected.applicant_status = "6"
    job_rejected.declined_at = timezone.now()
    job_rejected.save()
    return redirect(reverse('applicantslist', args=[job.id]))
