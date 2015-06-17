#coding=utf-8

from django.contrib import admin


from biz.floating.models import Floating


class FloatingAdmin(admin.ModelAdmin):
    list_display = ("id", "ip", "status", "instance","user")



admin.site.register(Floating, FloatingAdmin)
