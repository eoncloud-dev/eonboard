#coding=utf-8

from django import forms
from django.contrib import admin

from biz.idc.models import DataCenter, UserDataCenter


class DataCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "host", "project", "user", "password")


class DataCenterChoiceField(forms.ModelChoiceField):
     def label_from_instance(self, obj):
         return "%s" % obj.name


class UserDataCenterAdminForm(forms.ModelForm):
    data_center = DataCenterChoiceField(queryset=DataCenter.objects.all()) 
    class Meta:
        model = UserDataCenter
        fields = "__all__"


class UserDataCenterAdmin(admin.ModelAdmin):
    form = UserDataCenterAdminForm
    list_display = ("user","data_center", "tenant_name", "keystone_user")


admin.site.register(DataCenter, DataCenterAdmin)
admin.site.register(UserDataCenter, UserDataCenterAdmin)
