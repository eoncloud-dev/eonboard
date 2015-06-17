#coding=utf-8

import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

from biz.idc.models import DataCenter as dc
from biz.account.models import UserProfile
from cloud.tasks import link_user_to_dc_task

class CloudUserCreateForm(UserCreationForm):
    e_messages = {
        'error_email': _("email address format error")
    }

    mobile = forms.CharField()
    user_type = forms.IntegerField()

    def clean_username(self):
        username = super(CloudUserCreateForm, self).clean_username()
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return username
        else:
            raise forms.ValidationError(self.e_messages['error_email'])

    def save(self, commit=True):
        user = super(CloudUserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['username']

        if commit:
            r = user.save()
            UserProfile.objects.create(user=user,
                            user_type=self.cleaned_data['user_type'],
                            mobile = self.cleaned_data['mobile'])
            
            link_user_to_dc_task.delay(user, dc.get_default());
        return user

