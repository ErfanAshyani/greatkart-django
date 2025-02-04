from django.utils.html import format_html
from django.contrib import admin
from .models import Account, UserProfile

from django.contrib.auth.admin import UserAdmin
class AccountAdmin(UserAdmin):
    #content display in http://127.0.0.1:8000/admin/accounts/account/
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
    #does not work
    list_displayـlinks = ('email','first_name','last_name')
    readonly_fields = ('last_login','date_joined')
    #decending -
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    #make password readonly
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumnail.short_description = "Profile Picture"
    list_display = ('thumnail','user','city','state','country')    
    

# Register your models here.
admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
