import json
import datetime
import urllib2
import requests
import oauth2 as oauth
import cgi

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
# from xmljson import badgerfish as bf
from lxml import etree
from xml.etree.ElementTree import fromstring
from json import dumps
from xmljson import badgerfish as bf
from xmljson import BadgerFish

from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, \
redirect, render_to_response

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from job.models import Job, Employee, Applicant, ApplicationTime, Messages, \
UsersMessage, MailedContent

from django.contrib.auth.models import User
from authenticate.models import FacebookUser, GoogleUser, \
LinkedinUser, InstagramUser, TwitterProfile, FacebookUserContact, GoogleUserContact, TwitterUserContact
from job.forms import UserForm, EmailForm, \
LinkedinEmailForm, TwitterEmailForm



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


def googleauth(request):
    googleclientid = settings.GOOGLE_CLIENT_ID
    auth_url = "https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcontacts.readonly%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&access_type=online&include_granted_scopes=true&state=state_parameter_passthrough_value&redirect_uri=http%3A%2F%2Flocalhost%3A8001%2Fhome&response_type=code&client_id=" + googleclientid
    return redirect(auth_url)


def get_google_token(code):
    try:
        access_token_url = 'https://accounts.google.com/o/oauth2/token'
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
        inspect_token = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + token
        user_data = requests.get(inspect_token)
        return user_data.json()
    except:
        return HttpResponse("Unable to get User Info")

def get_google_user_contacts(email, token):
    contacts_url = "https://www.google.com/m8/feeds/contacts/" + email + "/full"
    params = {
        'access_token' : token,
    }
    google_user_contacts = requests.get(contacts_url, params=params)
    google_contacts = dumps(bf.data(fromstring(google_user_contacts.content)))
    google_contacts = json.loads(google_contacts)
    user = User.objects.get(username=email)
    for key, cont in google_contacts.items():
        for count_key, count in cont.items():
            if "{http://www.w3.org/2005/Atom}entry" in count_key:
                for list_item in count:
                    for elm_key, elm in list_item.items():
                        if "id" in elm_key:
                            if "$" in elm.keys():
                                print elm['$']
                                user_id = elm['$']
                        if "title" in elm_key:
                            if "$" in elm.keys():
                                print elm['$']
                                user_name = elm['$']
                            else:
                                user_name = ""
                        if "phoneNumber" in elm_key:
                            try:
                                if "$" in elm.keys():
                                    print elm['$']
                                    user_contact = elm['$']
                            except:
                                if "$" in elm[0].keys():
                                    print elm[0]['$']
                                    user_contact = elm[0]['$']
                        if "email" in elm_key:
                            if "@address" in elm.keys():
                                print elm['@address']
                                user_email = elm['@address']
                            g_contacts = GoogleUserContact.objects.create(
                                google_user=user,
                                contact_id=user_id,
                                name=user_name,
                                email=user_email,
                                phone=user_contact,
                            )
        return google_user_contacts

def socialgoogle(request):
    auth_code = request.GET.get('code', '')
    token = get_google_token(auth_code) #calling a function for access token.
    user_info = get_google_user_info(token) # calling a function for user info.
    print user_info
    userid = user_info['id']
    email = user_info['email']
    if User.objects.filter(email=email, username=email).exists():
        new_user = User.objects.get(email=email)
        if GoogleUser.objects.filter(google_userid=userid).exists():
            user = User.objects.get(email=email)
            if GoogleUserContact.objects.filter(google_user=user).exists():
                pass
            else:
                user_contacts = get_google_user_contacts(email, token)
            login(request, user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
                pass
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
                pass
        else:
            new_googleuser = GoogleUser.objects.create(
                google_user=new_user,
                google_userid=userid,
                email=email,
                )
            new_googleuser.save()
            if GoogleUserContact.objects.filter(google_user=user).exists():
                pass
            else:
                user_contacts = get_google_user_contacts(email, token)
            login(request, new_user)
            if request.user.is_staff:
                return redirect(reverse('employeepage', args=[request.user.id]))
                pass
            else:
                return redirect(reverse('applicantpage', args=[request.user.id]))
                pass
        message = "logged in successfully."
        return render(request, 'social/dashboard_google.html', {'user_info': user_info, 'message': message})
    else:
        new_user = User.objects.create_user(
            username=email,
            email=email,
            )
        new_user.save()
        new_googleuser = GoogleUser.objects.create(
            google_user=new_user,
            google_userid=userid,
            email=email,
            )
        new_googleuser.save()
        if GoogleUserContact.objects.filter(google_user=user).exists():
            pass
        else:
            user_contacts = get_google_user_contacts(email, token)
        login(request, new_user)
        if request.user.is_staff:
            return redirect(reverse('employeepage', args=[request.user.id]))
            pass
        else:
            return redirect(reverse('applicantpage', args=[request.user.id]))
            pass


def facebookauth(request):
    fb_auth_url = "https://www.facebook.com/v2.8/dialog/oauth?client_id=237086353424892&redirect_uri=http%3A%2F%2Flocalhost:8001%2Fsocial_facebook&granted_scopes=true&scope=email,user_friends"
    return redirect(fb_auth_url)


def get_fb_access_token(code):
    try:
        url = 'https://graph.facebook.com/v2.8/oauth/access_token?client_id=' + settings.FACEBOOK_CLIENT_ID + '&redirect_uri=http%3A%2F%2Flocalhost:8001%2Fsocial_facebook&client_secret=' + settings.FACEBOOK_CLIENT_SECRET + '&code=' + code + '&read_custom_friendlists=true'
        serialized_data = urllib2.urlopen(url).read()
        data = json.loads(serialized_data)
        return data['access_token']
    except:
        return HttpResponse("Unable to get Access Token")


def get_fb_user_id(access_token):
    try:
        inspect_url = 'https://graph.facebook.com/debug_token?input_token=' + access_token + '&access_token=' + settings.FACEBOOK_ACCESS_TOKEN
        user_data = urllib2.urlopen(inspect_url).read()
        return json.loads(user_data)
    except:
        return HttpResponse("Unable to get Application Id")


def get_fb_user_info(userid, access_token):
    try:
        detail_url = 'https://graph.facebook.com/v2.8/' + userid + '?&access_token=' + access_token + '&fields=id,name,birthday,email'
        user_detail = requests.get(detail_url)
        user_data = user_detail.json()
        return user_data
    except:
        return HttpResponse("Unable to get User Information")

def get_fb_user_friends(userid, access_token):
    try:
        friends_url = 'https://graph.facebook.com/v2.8/' + userid + '/taggable_friends?&limit=500&access_token=' + access_token + '&fields=id,name,about,age_range,birthday,email,taggable_friends'
        user_friends = requests.get(friends_url)
        friends_data = user_friends.json()
        return friends_data
    except:
        return HttpResponse("Unable to get User Information")


def socialfacebook(request):
    code = request.GET.get('code', '')
    access_token = get_fb_access_token(code) # call for access token with auth code.
    fb_user_id = get_fb_user_id(access_token) # call for userid and appid with access token.
    uid = fb_user_id['data']
    userid = uid['user_id']
    user_info = get_fb_user_info(userid, access_token) # call for fb user info with userid.
    print user_info
    if "email" in user_info.keys():
        email = user_info['email']
        if User.objects.filter(email=email, username=email).exists():
            new_user = User.objects.get(email=email)
            if FacebookUserContact.objects.filter(facebook_user=new_user).exists():
                pass
            else:
                user_friends = get_fb_user_friends(userid, access_token) # call for fb user friends with userid.
                friends_list = user_friends['data']
                for friend in friends_list:
                    FacebookUserContact.objects.create(
                        facebook_user=new_user,
                        contact_id=friend['id'],
                        name=friend['name']
                    )
            if FacebookUser.objects.filter(facebook_userid=userid).exists():
                pass
            else:
                new_facebookuser = FacebookUser.objects.create(
                    facebook_user=new_user,
                    facebook_userid=userid,
                    email=email,
                )
        else:
            new_user = User.objects.create_user(
                username=email,
                email=email,
            )
            new_facebookuser = FacebookUser.objects.create(
                facebook_user=new_user,
                facebook_userid=userid,
                email=email,
            )
            user_friends = get_fb_user_friends(userid, access_token) # call for fb user friends with userid.
            friends_list = user_friends['data']
            for friend in friends_list:
                FacebookUserContact.objects.create(
                    facebook_user=new_user,
                    contact_id=friend['id'],
                    name=friend['name']
                )
        login(request, new_user)
        if request.user.is_staff:
            return redirect(reverse('employeepage', args=[request.user.id]))
            pass
        else:
            return redirect(reverse('applicantpage', args=[request.user.id]))
            pass
    else:
        if FacebookUser.objects.filter(facebook_userid=userid).exists():
            facebook_user = FacebookUser.objects.get(facebook_userid=userid)
            if facebook_user.email is not None:
                user = User.objects.get(email=facebook_user.email)
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                    pass
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
                    pass
            else:
                pass
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
                user_friends = get_fb_user_friends(userid, access_token) # call for fb user friends with userid.
                friends_list = user_friends['data']
                for friend in friends_list:
                    FacebookUserContact.objects.create(
                        facebook_user=new_user,
                        contact_id=friend['id'],
                        name=friend['name']
                    )
            message = "email updated successfully."
            return render(request, 'social/dashboard_facebook.html', {'message': message})
        else:
            message = "Please fill the valid details."
            return render(request, 'social/email_form.html', {'form': form, 'message': message})
    else:
        message = ""
        return render(request, 'social/email_form.html', {'form' : form, 'message': message})


def instaauth(request):
    insta_auth_url = "https://api.instagram.com/oauth/authorize/?client_id=" + settings.INSTAGRAM_CLIENT_ID + "&redirect_uri=http://localhost:8001/main&response_type=code"
    return redirect(insta_auth_url)


def get_insta_auth(request):
    code = request.GET.get('code', '')
    print code
    access_token_req_url = 'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id' : settings.INSTAGRAM_CLIENT_ID,
        'client_secret' : settings.INSTAGRAM_CLIENT_SECRET,
        'grant_type' : 'authorization_code',
        'redirect_uri' : 'http://localhost:8001/main',
        'code' : code,
        }
    access_token = requests.post(access_token_req_url, data= data)
    print dir(access_token)
    token = access_token.json()
    print token
    user = token['user']
    uid = user['id']
    username = user['username']
    print uid
    print username
    return render(request, 'social/dashboard_instagram.html', {'token': token})


def linkedinauth(request):
    linkedinclientid = settings.LINKEDIN_CLIENT_ID
    linkedin_auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=" + linkedinclientid + "&redirect_uri=http%3A%2F%2Flocalhost:8001/linkedin&state=123456789&scope=r_basicprofile%20r_emailaddress"
    return redirect(linkedin_auth_url)


def get_linkedin_access_token(code):
    access_token_req_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    data = {
        'client_id' : settings.LINKEDIN_CLIENT_ID,
        'client_secret' : settings.LINKEDIN_CLIENT_SECRET,
        'grant_type' : 'authorization_code',
        'redirect_uri' : 'http://localhost:8001/linkedin',
        'code' : code,
        }
    access_token = requests.post(access_token_req_url, data= data)
    token = access_token.json()
    print token
    real_access_token = token['access_token']
    return real_access_token


def get_linkedin_user_info(access_token):
    user_info_url = 'https://api.linkedin.com/v1/people/~:(id,email-address,first-name,last-name,picture-url,num-connections,connections)?format=json'
    data = {
        'Host' : 'api.linkedin.com',
        'Connection' : 'Keep-Alive',
        }
    headers = {
        'Authorization' : 'Bearer ' + access_token,
        }
    info = requests.get(user_info_url, data = data, headers = headers)
    return info.json()


def get_linkedin_auth(request):
    code = request.GET.get('code', '')
    access_token = get_linkedin_access_token(code) # func call to get authenticated linkedin user access token.
    user_info = get_linkedin_user_info(access_token) #func call to get authenticated linkedin user info.
    userid = user_info['id']
    print user_info
    if "emailAddress" in user_info.keys():
        email = user_info['emailAddress']
        if User.objects.filter(email=email, username=email).exists():
            user = User.objects.get(email=email)
            if LinkedinUser.objects.filter(linkedin_userid=userid).exists():
                login(request, user)
                message = "logged in successfully."
            else:
                new_linkedinuser = LinkedinUser.objects.create(
                    linkedin_user=user,
                    linkedin_userid=userid,
                    email=email,
                )
                new_linkedinuser.save()
                login(request, user)
        else:
            new_user = User.objects.create_user(
                username=email,
                email=email,
                )
            new_user.save()
            new_linkedinuser = LinkedinUser.objects.create(
                linkedin_user=user,
                linkedin_userid=userid,
                email=email,
                )
            new_linkedinuser.save()
        login(request, user)
        if request.user.is_staff:
            return redirect(reverse('employeepage', args=[request.user.id]))
            pass
        else:
            return redirect(reverse('applicantpage', args=[request.user.id]))
            pass
    else:
        if LinkedinUser.objects.filter(linkedin_userid=user_info['id']).exists():
            linkedin_user = LinkedinUser.objects.get(linkedin_userid=user_info['id'])
            if linkedin_user.email != "":
                user = User.objects.get(email=linkedin_user.email)
                login(request, user)
                if request.user.is_staff:
                    return redirect(reverse('employeepage', args=[request.user.id]))
                    pass
                else:
                    return redirect(reverse('applicantpage', args=[request.user.id]))
                    pass
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
            new_user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                )
            new_user.save()
            linkedin_user_email = LinkedinUser.objects.get(linkedin_userid= form.cleaned_data['linkedin_userid'])
            linkedin_user_email.linkedin_user = new_user
            linkedin_user_email.email = form.cleaned_data['email']
            linkedin_user_email.save()
            message = "email updated successfully."
            return render(request, 'social/dashboard_linkedin.html', {'message': message})
        else:
            message = "Please fill the valid details."
            return render(request, 'social/linkedin_email_form.html', {'form': form, 'message': message})
    else:
        message = ""
        return render(request, 'social/linkedin_email_form.html', {'form' : form, 'message': message})


@login_required(login_url="/login/")
def redirecturl(request):
    return render(request, 'social/dashboard.html')


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


consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token?include_email=true'
authenticate_url = 'https://api.twitter.com/oauth/authenticate'
authorize_url = 'https://api.twitter.com/oauth/authorize'

def twitter_login(request):
    # Get a request token from Twitter.
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")
    # Store the request token in a session for later use.
    request.session['request_token'] = dict(cgi.parse_qsl(content))
    # Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s" % (authenticate_url,
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
    resp, content = client.request(access_token_url, "GET")
    access_token = dict(cgi.parse_qsl(content))
    print access_token
    followers_ids_list = oauth_req('https://api.twitter.com/1.1/followers/ids.json', access_token['oauth_token'], access_token['oauth_token_secret'])
    print followers_ids_list
    followers_ids_list = json.loads(followers_ids_list)
    credentials = oauth_req('https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true', access_token['oauth_token'], access_token['oauth_token_secret'])
    print credentials
    credentials = json.loads(credentials)
    print credentials['email']
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
