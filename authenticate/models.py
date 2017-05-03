from __future__ import unicode_literals

import datetime
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class LinkedinUser(models.Model):
    linkedin_user = models.ForeignKey(User, blank=True, null=True)
    linkedin_userid = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.linkedin_userid


class InstagramUser(models.Model):
    instagram_user = models.ForeignKey(User, blank=True, null=True)
    instagram_userid = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.instagram_user


class FacebookUser(models.Model):
    facebook_user = models.ForeignKey(User, blank=True, null=True)
    facebook_userid = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.facebook_userid

class GoogleUser(models.Model):
    google_user = models.ForeignKey(User, blank=True, null=True)
    google_userid = models.CharField(max_length=200)
    name = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.google_user

class GoogleUserContact(models.Model):
    google_user = models.ForeignKey(User)
    contact_id = models.CharField(max_length=255)
    name = models.CharField(max_length=55)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class FacebookUserContact(models.Model):
    facebook_user = models.ForeignKey(User)
    contact_id = models.CharField(max_length=255)
    name = models.CharField(max_length=55)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class TwitterUserContact(models.Model):
    twitter_user = models.ForeignKey(User)
    contact_id = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=55, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)

    def __int__(self):
        return self.contact_id

class TwitterProfile(models.Model):
    user = models.ForeignKey(User)
    twitter_user_id = models.CharField(max_length=255, default=0)
    email = models.EmailField(max_length=200, blank=True)

    def __int__(self):
        return self.user
