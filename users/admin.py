from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .import models

@admin.register(models.User)
##admin.site.register(models.User,CustomUserAdmin)
class CustomUserAdmin(UserAdmin):
    fieldsets =UserAdmin.fieldsets + (("Custom Profile", {"fields":("avatar","gender","bio","birthdate","language","currency","superhost")}),)
    
