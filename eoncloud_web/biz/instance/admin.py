#coding=utf-8

from django.contrib import admin

from biz.instance.models import Instance, Flavor


class InstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "public_ip", "create_date","user")


class FlavorAdmin(admin.ModelAdmin):
    list_display = ("name", "cpu", "memory")



admin.site.register(Instance, InstanceAdmin)
admin.site.register(Flavor, FlavorAdmin)
