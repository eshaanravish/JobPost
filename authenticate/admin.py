from django.contrib import admin

# Register your models here.
from .models import FacebookUser, GoogleUser, LinkedinUser, InstagramUser, \
TwitterProfile, GoogleUserContact, FacebookUserContact, TwitterUserContact



class LinkedinUserAdmin(admin.ModelAdmin):
    list_display = ('linkedin_user', 'linkedin_userid', 'email')

admin.site.register(LinkedinUser, LinkedinUserAdmin)

class InstagramUserAdmin(admin.ModelAdmin):
    list_display = ('instagram_user', 'instagram_userid', 'email')

admin.site.register(InstagramUser, InstagramUserAdmin)

class FacebookUserAdmin(admin.ModelAdmin):
    list_display = ('facebook_user', 'facebook_userid', 'email')

admin.site.register(FacebookUser, FacebookUserAdmin)

class FacebookUserContactAdmin(admin.ModelAdmin):
    list_display = ('facebook_user', 'name', 'email')

admin.site.register(FacebookUserContact, FacebookUserContactAdmin)

class GoogleUserAdmin(admin.ModelAdmin):
    list_display = ('google_user', 'google_userid', 'email')

admin.site.register(GoogleUser, GoogleUserAdmin)

class GoogleUserContactAdmin(admin.ModelAdmin):
    list_display = ('google_user', 'name', 'email')

admin.site.register(GoogleUserContact, GoogleUserContactAdmin)

class TwitterUserContactAdmin(admin.ModelAdmin):
    list_display = ('twitter_user', 'screen_name', 'email')

admin.site.register(TwitterUserContact, TwitterUserContactAdmin)

class TwitterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter_user_id', 'email')

admin.site.register(TwitterProfile, TwitterProfileAdmin)
