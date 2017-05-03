import json
import datetime
import urllib2
import requests
import oauth2 as oauth
import cgi

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from json import dumps

from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, \
redirect, render_to_response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from django.contrib.auth.models import User

from job.models import Job, Employee, Applicant, ApplicationTime, Messages, \
UsersMessage, MailedContent

from authenticate.models import FacebookUser, GoogleUser, \
LinkedinUser, InstagramUser, TwitterProfile, FacebookUserContact, \
GoogleUserContact, TwitterUserContact

from job.forms import UserForm, EmailForm, \
LinkedinEmailForm, TwitterEmailForm


def user_existance_check(request):
    if request.is_ajax():
        email = request.GET.get('email', '')
        if User.objects.filter(username=email).exists():
            user = User.objects.get(email=email)
            if GoogleUser.objects.filter(google_user=user).exists() or FacebookUser.objects.filter(facebook_user=user).exists() or LinkedinUser.objects.filter( linkedin_user=user).exists() or TwitterProfile.objects.filter(user=user).exists():
                response = {'data': True, 'status': True}
            else:
                response = {'data': False, 'status': True}
            return HttpResponse(json.dumps(response))
        else:
            response = {'status': False}
            return HttpResponse(json.dumps(response))
    else:
        Http404


def homepage(request):
    if request.method == "POST":
        form = UserForm(request.POST, use_required_attribute= False)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['email']).exists():
                user = User.objects.get(username=form.cleaned_data['email'])
                login(request, user)
                return HttpResponseRedirect(reverse('applicantpage', args=[user.id]))
            else:
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                )
                user.save()
                login(request, user)
                applier = Applicant.objects.create()
                applier.username = request.user
                applier.save()
                return HttpResponseRedirect(reverse('applicantpage', args=[user.id]))
        else:
            error_message = "Please fill the valid details."
            return render(request, 'social/home.html', {'form': form, 'error_message': error_message})
    else:
        error_message = ""
        form = UserForm(request.POST, use_required_attribute= False)
        return render(request, 'social/home.html', {'form': form, 'error_message': error_message})

# Google Authentication

# Google endpoints
google_auth_url = "https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcontacts.readonly%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&access_type=online&include_granted_scopes=true&state=state_parameter_passthrough_value&redirect_uri=http%3A%2F%2Flocalhost%3A8001%2Fhome&response_type=code&client_id=" + settings.GOOGLE_CLIENT_ID
google_access_token_url = 'https://accounts.google.com/o/oauth2/token'
google_inspect_token = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token='
google_contacts_url = "https://www.google.com/m8/feeds/contacts/"

def googleauth(request):
    return redirect(google_auth_url)


def get_google_token(code):
    try:
        access_token_url = google_access_token_url
        data = {
            'grant_type' : 'authorization_code',
            'redirect_uri' : 'http://localhost:8001/home',
            'client_id' : settings.GOOGLE_CLIENT_ID,
            'client_secret' : settings.GOOGLE_CLIENT_SECRET,
            'code' : code,
            'scope' : 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.readonly'
            }
        headers = {
            'Host': 'accounts.google.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            }
        access_token = requests.post(access_token_url, data= data, headers= headers)
        token_data = access_token.json()
        return token_data['access_token']
    except:
        return HttpResponse("Unable to get Access Token")


def get_google_user_info(token):
    try:
        inspect_token = google_inspect_token + token
        user_data = requests.get(inspect_token)
        return user_data.json()
    except:
        return HttpResponse("Unable to get User Info")


def get_google_user_contacts(email, token):
    contacts_url = google_contacts_url + email + "/full?alt=json"
    params = {
        'access_token' : token,
    }
    google_user_contacts = requests.get(contacts_url, params=params)
    google_contacts = google_user_contacts.json()
    user = User.objects.get(username=email)
    contacts_dict = google_contacts['feed']
    entry = contacts_dict['entry']
    for list_item in entry:
        # id
        contact_id = list_item['id']
        user_id = contact_id['$t']
        # Name
        try:
            contact_title = list_item['title']
            user_name = contact_title['$t']
        except:
            user_name = ""
        # Phone Number
        try:
            contact_phone = list_item['gd$phoneNumber']
            user_phone = contact_phone['$t']
        except:
            user_phone = ""
        # Email address
        try:
            contact_email = list_item['gd$email']
            user_email = contact_email['address']
        except:
            user_email = ""
        g_contacts = GoogleUserContact.objects.create(
            google_user=user,
            contact_id=user_id,
            name=user_name,
            email=user_email,
            phone=user_phone,
        )
    return google_user_contacts


def create_google_user(userid, email):
    user = User.objects.get(username=email)
    new_googleuser = GoogleUser.objects.create(
        google_user=user,
        google_userid=userid,
        email=email,
        )
    return new_googleuser


def socialgoogle(request):
    auth_code = request.GET.get('code', '')
    #calling a function for access token.
    token = get_google_token(auth_code) 
    # calling a function for user info.
    user_info = get_google_user_info(token) 
    userid = user_info['id']
    email = user_info['email']
    if User.objects.filter(email=email, username=email).exists():
        user = User.objects.get(email=email)
        if GoogleUser.objects.filter(google_userid=userid).exists():
            if GoogleUserContact.objects.filter(google_user=user).exists():
                pass
            else:
                # function call to create objects for contacts of google user.
                user_contacts = get_google_user_contacts(email, token)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            new_google_user = create_google_user(userid, email)
            # function call to create objects for contacts of google user.
            user_contacts = get_google_user_contacts(email, token)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
    else:
        user = User.objects.create_user(
            username=email,
            email=email,
            )
        # function call to create GoogleUser objects.
        new_google_user = create_google_user(userid, email)
        login(request, user)
        if request.user.is_staff:
            return redirect(reverse('employeepage', args=[request.user.id]))
        else:
            return redirect(reverse('applicantpage', args=[request.user.id]))

# Facebook Authentication

# Facebook endpoints
fb_auth_url = "https://www.facebook.com/v2.8/dialog/oauth?client_id=237086353424892&redirect_uri=http%3A%2F%2Flocalhost:8001%2Fsocial_facebook&granted_scopes=true&scope=email,user_friends"
fb_access_token_url = 'https://graph.facebook.com/v2.8/oauth/access_token?client_id='
fb_inspect_url = 'https://graph.facebook.com/debug_token?input_token='
fb_detail_url = 'https://graph.facebook.com/v2.8/'
fb_friends_url = 'https://graph.facebook.com/v2.8/'

def facebookauth(request):
    return redirect(fb_auth_url)


def get_fb_access_token(code):
    try:
        url = fb_access_token_url + settings.FACEBOOK_CLIENT_ID + '&redirect_uri=http%3A%2F%2Flocalhost:8001%2Fsocial_facebook&client_secret=' + settings.FACEBOOK_CLIENT_SECRET + '&code=' + code + '&read_custom_friendlists=true'
        serialized_data = urllib2.urlopen(url).read()
        data = json.loads(serialized_data)
        return data['access_token']
    except:
        return HttpResponse("Unable to get Access Token")


def get_fb_user_id(access_token):
    try:
        inspect_url = fb_inspect_url + access_token + '&access_token=' + settings.FACEBOOK_ACCESS_TOKEN
        user_data = urllib2.urlopen(inspect_url).read()
        return json.loads(user_data)
    except:
        return HttpResponse("Unable to get Application Id")


def get_fb_user_info(userid, access_token):
    try:
        detail_url = fb_detail_url + userid + '?&access_token=' + access_token + '&fields=id,name,birthday,email'
        user_detail = requests.get(detail_url)
        user_data = user_detail.json()
        return user_data
    except:
        return HttpResponse("Unable to get User Information")


def get_fb_user_friends(user, userid, access_token):
    try:
        friends_url = fb_friends_url + userid + '/taggable_friends?&limit=500&access_token=' + access_token + '&fields=id,name,about,age_range,birthday,email,taggable_friends'
        user_friends = requests.get(friends_url)
        friends_data = user_friends.json()
        friends_list = friends_data['data']
        for friend in friends_list:
            fb_contacts = FacebookUserContact.objects.create(
                facebook_user=user,
                contact_id=friend['id'],
                name=friend['name']
            )
        return friends_data
    except:
        return HttpResponse("Unable to get User Information")


def create_fb_user_object(user_info, userid, access_token):
    email = user_info['email']
    user = User.objects.create_user(
        username=email,
        email=email,
    )
    applicant = Applicant.objects.create(
        username=user,
    )
    new_facebookuser = FacebookUser.objects.create(
        facebook_user=user,
        facebook_userid=user_info['id'],
        email=email,
    )
    # call for fb user friends with userid.
    user_friends = get_fb_user_friends(user, userid, access_token) 
    return user_friends

def socialfacebook(request):
    code = request.GET.get('code', '')
    # call for access token with auth code.
    access_token = get_fb_access_token(code) 
    # call for userid and appid with access token.
    fb_user_id = get_fb_user_id(access_token) 
    uid = fb_user_id['data']
    userid = uid['user_id']
    # call for fb user info with userid.
    user_info = get_fb_user_info(userid, access_token)
    if "email" in user_info.keys():
        email = user_info['email']
        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            user = User.objects.get(username=email)
            create_user = create_fb_user_object(user_info, userid, access_token)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
    else:
        if FacebookUser.objects.filter(facebook_userid=userid).exists():
            fb_user = FacebookUser.objects.get(facebook_userid=userid)
            user = User.objects.get(username=fb_user.email)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            facebook_user = FacebookUser.objects.create(
                facebook_userid=user_info['id'],
                name=user_info['name'],
                )
            message = ""
            form = EmailForm(instance = facebook_user)
            return render(request, 'social/email_form.html', {'form' : form, 'message': message})


def get_email(request):
    form = EmailForm(request.POST, use_required_attribute= False)
    if request.method == "POST":
        if form.is_valid():
            new_user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                )
            new_user.save()
            facebook_user_email = FacebookUser.objects.get(facebook_userid= form.cleaned_data['facebook_userid'])
            facebook_user_email.facebook_user = new_user
            facebook_user_email.email = form.cleaned_data['email']
            facebook_user_email.save()
            if FacebookUserContact.objects.filter(facebook_user=new_user).exists():
                pass
            else:
                # call for fb user friends with userid.
                user_friends = get_fb_user_friends(userid, access_token) 
                friends_list = user_friends['data']
                for friend in friends_list:
                    FacebookUserContact.objects.create(
                        facebook_user=new_user,
                        contact_id=friend['id'],
                        name=friend['name']
                    )
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            message = "Please fill the valid details."
            return render(request, 'social/email_form.html', {'form': form, 'message': message})
    else:
        message = ""
        return render(request, 'social/email_form.html', {'form' : form, 'message': message})

# Instagram Authentication

# Instagram endpoints
insta_auth_url = "https://api.instagram.com/oauth/authorize/?client_id=" + settings.INSTAGRAM_CLIENT_ID + "&redirect_uri=http://localhost:8001/main&response_type=code"
access_token_req_url = 'https://api.instagram.com/oauth/access_token'

def instaauth(request):
    return redirect(insta_auth_url)


def get_insta_auth(request):
    code = request.GET.get('code', '')
    data = {
        'client_id' : settings.INSTAGRAM_CLIENT_ID,
        'client_secret' : settings.INSTAGRAM_CLIENT_SECRET,
        'grant_type' : 'authorization_code',
        'redirect_uri' : 'http://localhost:8001/main',
        'code' : code,
        }
    access_token = requests.post(access_token_req_url, data= data)
    token = access_token.json()
    user = token['user']
    uid = user['id']
    username = user['username']
    return render(request, 'social/dashboard_instagram.html', {'token': token})

# LinkedIn Authentication

# LinkedIn endpoints
linkedin_auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=" + settings.LINKEDIN_CLIENT_ID + "&redirect_uri=http%3A%2F%2Flocalhost:8001/linkedin&state=123456789&scope=r_basicprofile%20r_emailaddress"
linkedin_access_token_req_url = 'https://www.linkedin.com/oauth/v2/accessToken'
linkedin_user_info_url = 'https://api.linkedin.com/v1/people/~:(id,email-address,first-name,last-name,picture-url,num-connections,connections)?format=json'

def linkedinauth(request):
    return redirect(linkedin_auth_url)


def get_linkedin_access_token(code):
    data = {
        'client_id' : settings.LINKEDIN_CLIENT_ID,
        'client_secret' : settings.LINKEDIN_CLIENT_SECRET,
        'grant_type' : 'authorization_code',
        'redirect_uri' : 'http://localhost:8001/linkedin',
        'code' : code,
        }
    access_token = requests.post(linkedin_access_token_req_url, data= data)
    token = access_token.json()
    real_access_token = token['access_token']
    return real_access_token


def get_linkedin_user_info(access_token):
    data = {
        'Host' : 'api.linkedin.com',
        'Connection' : 'Keep-Alive',
        }
    headers = {
        'Authorization' : 'Bearer ' + access_token,
        }
    info = requests.get(linkedin_user_info_url, data = data, headers = headers)
    return info.json()


def create_linked_user(user,user_info):
    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            )
        new_linkedinuser = LinkedinUser.objects.create(
            linkedin_user=user,
            linkedin_userid=userid,
            email=email,
            )
        return new_linkedinuser
    except:
        return HttpResponse("Unable to get User")

def get_linkedin_auth(request):
    code = request.GET.get('code', '')
    # func call to get authenticated linkedin user access token.
    access_token = get_linkedin_access_token(code) 
    #func call to get authenticated linkedin user info.
    user_info = get_linkedin_user_info(access_token) 
    userid = user_info['id']
    if "emailAddress" in user_info.keys():
        email = user_info['emailAddress']
        if User.objects.filter(email=email, username=email).exists():
            user = User.objects.get(email=email)
            if LinkedUser.objects.filter(linkedin_user=user).exists():
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
            else:
                new_linkedinuser = LinkedinUser.objects.create(
                    linkedin_user=user,
                    linkedin_userid=userid,
                    email=email,
                    )
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            linked_user = create_linked_user(user,user_info)
            user = User.objects.get(email=email)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
    else:
        if LinkedinUser.objects.filter(linkedin_userid=user_info['id']).exists():
            linkedin_user = LinkedinUser.objects.get(linkedin_userid=user_info['id'])
            if linkedin_user.email != "":
                user = User.objects.get(email=linkedin_user.email)
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
            else:
                pass
        else:
            linkedin_user = LinkedinUser.objects.create(
                linkedin_userid=user_info['id'],
                name=user_info['firstName'],
                )
        message = ""
        form = LinkedinEmailForm(instance = linkedin_user)
        return render(request, 'social/linkedin_email_form.html', {'form' : form, 'message': message})


def get_linkedin_user_email(request):
    form = LinkedinEmailForm(request.POST, use_required_attribute= False)
    if request.method == "POST":
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                )
            new_user.save()
            linkedin_user_email = LinkedinUser.objects.get(linkedin_userid= form.cleaned_data['linkedin_userid'])
            linkedin_user_email.linkedin_user = new_user
            linkedin_user_email.email = form.cleaned_data['email']
            linkedin_user_email.save()
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
        else:
            message = "Please fill the valid details."
            return render(request, 'social/linkedin_email_form.html', {'form': form, 'message': message})
    else:
        message = ""
        return render(request, 'social/linkedin_email_form.html', {'form' : form, 'message': message})


def userauthenticate(request):
    email = request.GET['email']
    if User.objects.filter(username__in = email).count() == 0:
        # do successful login.
        username = email
        password = email
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard/')
                pass
            else:
                error_message = "You have provided invalid credentials."
        user = User.objects.get(username__in = email)
        login(request, user)
        return redirect('/')
    else:
        user = User.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=email,
            )
        user.save()
        login(request, user)
        return redirect('/dashboard/')

# Twitter Authentication

consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

# Twitter endpoints

twitter_request_token_url = 'https://api.twitter.com/oauth/request_token'
twitter_access_token_url = 'https://api.twitter.com/oauth/access_token?include_email=true'
twitter_authenticate_url = 'https://twitter.com/oauth/authenticate'

def twitter_login(request):
    # Get a request token from Twitter.
    resp, content = client.request(twitter_request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")
    # Store the request token in a session for later use.
    request.session['request_token'] = dict(cgi.parse_qsl(content))
    # Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s" % (twitter_authenticate_url,
        request.session['request_token']['oauth_token'])
    return redirect(url)


@login_required
def twitter_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    consumer = oauth.Consumer(key=settings.TWITTER_TOKEN, secret=settings.TWITTER_SECRET)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content


def twitter_authenticated(request):
    # Use the request token in the session to build a new client.
    token = oauth.Token(request.session['request_token']['oauth_token'],
        request.session['request_token']['oauth_token_secret'])
    token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)
    # Request the authorized access token from Twitter.
    resp, content = client.request(twitter_access_token_url, "GET")
    access_token = dict(cgi.parse_qsl(content))
    followers_ids_list = oauth_req('https://api.twitter.com/1.1/followers/ids.json', access_token['oauth_token'], access_token['oauth_token_secret'])
    followers_ids_list = json.loads(followers_ids_list)
    credentials = oauth_req('https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true', access_token['oauth_token'], access_token['oauth_token_secret'])
    credentials = json.loads(credentials)
    user_email = credentials['email']
    # Lookup the user or create them if they don't exist.
    if User.objects.filter(email=user_email).exists():
        user = User.objects.get(email=user_email)
        if TwitterProfile.objects.filter(user=user).exists():
            twitter_profile = TwitterProfile.objects.get(user=user)
            if twitter_profile.email != "":
                if TwitterUserContact.objects.filter(twitter_user=user).exists():
                    pass
                else:
                    for friends_id in followers_ids_list['ids']:
                        twitter_contacts = TwitterUserContact.objects.create(
                            twitter_user=user,
                            contact_id=friends_id
                        )
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                    pass
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
                    pass
            else:
                #redirect to the email req page.
                form = TwitterEmailForm(instance=twitter_profile)
                return render(request,'social/twitter_email_form.html', {'form': form})
        else:
            profile = TwitterProfile.objects.create(
                user=user,
                twitter_user_id=access_token['user_id'],
                email=user_email,
                )
            for friends_id in followers_ids_list['ids']:
                twitter_contacts = TwitterUserContact.objects.create(
                    twitter_user=user,
                    contact_id=friends_id
                )
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
                pass
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
                pass
    else:
        user = User.objects.create_user(
            username=user_email,
            email=user_email,
        )
        twitter_profile = TwitterProfile.objects.create(
            user=user,
            twitter_user_id=access_token['user_id'],
            email=user_email,
        )
        if "email" in access_token.keys():
            profile.email = access_token['email']
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
                pass
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
                pass
        else:
            #redirect to email req page.
            form = TwitterEmailForm(instance=twitter_profile)
            return render(request,'social/twitter_email_form.html', {'form': form})


def get_twitter_user_email(request):
    if request.method == "POST":
        form = TwitterEmailForm(request.POST)
        if form.is_valid():
            twitter_user_profile = TwitterProfile.objects.get(user=form.cleaned_data['user'])
            twitter_user_profile.username = form.cleaned_data['email']
            twitter_user_profile.email = form.cleaned_data['email']
            twitter_user_profile.save()
            user = User.objects.get(username=form.cleaned_data['email'])
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
                pass
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
                pass
        else:
            message = "Please fill the valid details."
            return render(request, 'social/twitter_email_form.html', {'form': form, 'message': message})
    else:
        form = TwitterEmailForm()
        message = ""
        return render(request, 'social/twitter_email_form.html', {'form' : form, 'message': message})
