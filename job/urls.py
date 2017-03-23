from django.conf.urls import url
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from .import views

from django.conf import settings
from django.views.static import serve


urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^signup/$', views.applicantsignup, name='adduser'),
    url(r'^login/$', views.applicantlogin, name='applicantlogin'),
    url(r'^(?P<jobs_id>[0-9]+)/messages/$', views.jobmessages, name='jobmessages'),
    url(r'^(?P<user_id>[0-9]+)/recruiter_jobs/$', views.recruiterrespectivejobs, name='recruiterrespectivejobs'),
    url(r'^logout/$', views.userlogout, name='logout'),
    url(r'^employeepage/(?P<user_id>[0-9]+)/$', views.employeepage, name='employeepage'),
    url(r'^login/(?P<user_id>[0-9]+)/profile/$', views.employeeprofile, name='employeeprofile'),
    url(r'^login/(?P<user_id>[0-9]+)/myjobs/$', views.employeejobs, name='employeejobs'),
    url(r'^login/(?P<user_id>[0-9]+)/profile/edit/$', views.editemployeeprofile, name='editemployeeprofile'),
    url(r'^employeepage/createjob/(?P<user_id>[0-9]+)/$', views.createjob, name='createjob'),
    url(r'^employeepage/list/(?P<jobs_id>[0-9]+)/$', views.applicantslist, name='applicantslist'),
    url(r'^employeepage/list/(?P<jobs_id>[0-9]+)/(?P<user_id>[0-9]+)/rejection/$', views.rejection, name='rejection'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/$', views.applicantpage, name='applicantpage'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/jobs$', views.alljobs, name='alljobs'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/like/(?P<jobs_id>[0-9]+)/$', views.likes, name='likes'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/unlike/(?P<jobs_id>[0-9]+)/$', views.unlikes, name='unlikes'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/list/(?P<jobs_id>[0-9]+)/$', views.usermessage, name='usermessage'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/profile/update/$', views.editapplicantprofile, name='editapplicantprofile'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/profile/$', views.applicantprofile, name='applicantprofile'),
    url(r'^applicantpage/(?P<user_id>[0-9]+)/profile/applied/$', views.appliedjobs, name='appliedjobs'),
    url(r'^(?P<user_id>[0-9]+)/profile/applied/(?P<jobs_id>[0-9]+)/job_status$', views.jobstatus, name='jobstatus'),
    url(r'^(?P<user_id>[0-9]+)/details/$', views.details, name='details'),
    url(r'^(?P<jobs_id>[0-9]+)/applicantpage/applied/$', views.applyjob, name='applyjob'),
    url(r'^employeepage/list/(?P<jobs_id>[0-9]+)/(?P<user_id>[0-9]+)/userdetail/(?P<applicant_id>[0-9]+)/$', views.userdetail, name='userdetail'),
    url(r'^employeepage/list/(?P<jobs_id>[0-9]+)/mailedcontent/(?P<job_applied_id>[0-9]+)/$', views.Mailedcontent, name='Mailedcontent'),
    url(r'^employeepage/(?P<user_id>[0-9]+)/(?P<jobs_id>[0-9]+)/delete/$', views.deletejob, name='deletejob'),
    url(r'^password_reset/$', password_reset, name= 'reset_password'),
    url(r'^password_reset/done/$', password_reset_done, name= 'password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name= 'password_reset_confirm'),
    url(r'^password/complete/$', password_reset_complete, name = 'password_reset_complete'),
    url(r'^([a-z]+)/$', views.location, name='location'),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
]
