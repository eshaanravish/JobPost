from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField
from django.core.mail import send_mail
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from job.models import Job, Employee, Applicant, ApplicationTime, Messages, UsersMessage
from django.forms import DurationField

from authenticate.models import FacebookUser, GoogleUser, LinkedinUser, InstagramUser, TwitterProfile


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder':'Password'})

class EmployeeForm(ModelForm):
    employee_pic = forms.ImageField(label='Select a file', help_text='max. 42 megabytes')

    class Meta:
        model = Employee
        fields = ('first_name', 'last_name','gender', 'email', 'address', 'contact', 'dob', 'joining_date', 'employee_pic')

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control'})
        self.fields['dob'].widget.attrs.update({'class': 'form-control'})
        self.fields['joining_date'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})
        self.fields['employee_pic'].widget.attrs.update({'class': 'form-control'})

class ApplicantForm(ModelForm):
    applicant_pic = forms.ImageField(label='Select a file', help_text='max. 42 megabytes')

    class Meta:
        model = Applicant
        fields = ('applicant_pic', 'firstname', 'lastname','applicant_gender', 'address', 'contact', 'dob', 'tenth_percentage', 'twelth_percentage', 'graduation', 'graduation_percentage', 'post_graduation', 'post_graduation_percentage', 'currently_working_with', 'current_position', 'experience', 'skills')

    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self.fields['applicant_pic'].widget.attrs.update({'class': 'form-control'})
        self.fields['applicant_pic'].required = True
        self.fields['firstname'].widget.attrs.update({'class': 'form-control', 'placeholder':'Firstname'})
        self.fields['firstname'].required = True
        self.fields['lastname'].widget.attrs.update({'class': 'form-control', 'placeholder':'Lastname'})
        self.fields['lastname'].required = True
        self.fields['applicant_gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['applicant_gender'].required = True
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'placeholder':'Address'})
        self.fields['address'].required = True
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder':'Contact'})
        self.fields['contact'].required = True
        self.fields['dob'].widget.attrs.update({'class': 'form-control', 'placeholder':'YYYY:MM:DD'})
        self.fields['dob'].required = True
        self.fields['tenth_percentage'].widget.attrs.update({'class': 'form-control', 'placeholder':'10th Percentage '})
        self.fields['tenth_percentage'].required = True
        self.fields['twelth_percentage'].widget.attrs.update({'class': 'form-control', 'placeholder':'12th Percentage'})
        self.fields['twelth_percentage'].required = True
        self.fields['graduation'].widget.attrs.update({'class': 'form-control', 'placeholder':'Graduation'})
        self.fields['graduation_percentage'].widget.attrs.update({'class': 'form-control', 'placeholder':'Graduation Percentage'})
        self.fields['post_graduation'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Graduation'})
        self.fields['post_graduation_percentage'].widget.attrs.update({'class': 'form-control', 'placeholder':'Post Graduation Percentage'})
        self.fields['currently_working_with'].widget.attrs.update({'class': 'form-control', 'placeholder':'Firm you are working with'})
        self.fields['current_position'].widget.attrs.update({'class': 'form-control', 'placeholder':'Currently working as'})
        self.fields['experience'].widget.attrs.update({'class': 'form-control', 'placeholder':'Experience in Months'})
        self.fields['skills'].widget.attrs.update({'class': 'form-control', 'placeholder':'Skills'})
        self.fields['skills'].required = True


class CreateJob(ModelForm):
    job_description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Job
        fields = ('job_title', 'job_description', 'job_location', 'job_skillsrequired','job_minqualification', 'job_experience', 'job_experience_months', 'job_valid_upto')

    def __init__(self, *args, **kwargs):
        super(CreateJob, self).__init__(*args, **kwargs)
        self.fields['job_title'].widget.attrs.update({'class': 'form-control', 'placeholder':'Title'})
        self.fields['job_description'].widget.attrs.update({'class': 'form-control', 'placeholder':'Description'})
        self.fields['job_location'].widget.attrs.update({'class': 'form-control', 'placeholder':'Location'})
        self.fields['job_skillsrequired'].widget.attrs.update({'class': 'form-control', 'placeholder':'Skills Required'})
        self.fields['job_minqualification'].widget.attrs.update({'class': 'form-control', 'placeholder':'Minimum Qualification Required'})
        self.fields['job_experience'].widget.attrs.update({'class': 'form-control'})
        self.fields['job_experience_months'].widget.attrs.update({'class': 'form-control'})
        self.fields['job_valid_upto'].widget.attrs.update({'class': 'form-control', 'placeholder':'YYYY:MM:DD'})

class MessagesForm(ModelForm):

    class Meta:
        model = Messages
        fields = ('name', 'email', 'body')

    def __init__(self, *args, **kwargs):
        super(MessagesForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder':'Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})
        self.fields['body'].widget.attrs.update({'class': 'form-control'})


class UsersMessageForm(ModelForm):

    class Meta:
        model = UsersMessage
        fields = ('name', 'job', 'body')

    def __init__(self, *args, **kwargs):
        super(UsersMessageForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['job'].widget.attrs.update({'class': 'form-control'})
        self.fields['body'].widget.attrs.update({'class': 'form-control', 'placeholder':'Feel free to message..'})


class MailtoApplicantForm(forms.Form):

    email = forms.EmailField()
    title = forms.ChoiceField(widget = forms.Select(), choices = ([
        ('Call for Telephonic Interview','Call for Telephonic Interview'),
        ('Call for Personal Interview','Call for Personal Interview'),
        ('Call for HR Interview','Call for HR Interview'),
        ('Joining Letter','Joining Letter'),
    ]), required = True,)
    body = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(MailtoApplicantForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['body'].widget.attrs.update({'class': 'form-control'})

class SearchForm(forms.Form):
    q = forms.CharField(max_length=255)


##############################################


# class SignUpForm(ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password')
#
#     def __init__(self, *args, **kwargs):
#         super(SignUpForm, self).__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder':'Username'})
#         self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})
#         self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder':'Password'})

class EmailForm(ModelForm):

    class Meta:
        model = FacebookUser
        fields = ('facebook_userid', 'name', 'email')

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.fields['facebook_userid'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})

class LinkedinEmailForm(ModelForm):

    class Meta:
        model = LinkedinUser
        fields = ('linkedin_userid', 'name', 'email')

    def __init__(self, *args, **kwargs):
        super(LinkedinEmailForm, self).__init__(*args, **kwargs)
        self.fields['linkedin_userid'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})

class TwitterEmailForm(ModelForm):

    class Meta:
        model = TwitterProfile
        fields = ('user', 'email', 'twitter_user_id')

    def __init__(self, *args, **kwargs):
        super(TwitterEmailForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})
        self.fields['twitter_user_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder':'EmailId'})
