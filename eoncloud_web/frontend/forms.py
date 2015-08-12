#coding=utf-8

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from biz.account.models import UserProfile


class CloudUserCreateForm(UserCreationForm):

    error_messages = UserCreationForm.error_messages.copy()

    error_messages.update({
        'duplicate_email': _("A user with that email already exists.")
    })

    email = forms.EmailField(label=_("Email"))
    mobile = forms.CharField(label=_("Mobile"))
    # user_type = forms.IntegerField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def save(self, commit=True):
        user = super(CloudUserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                mobile=self.cleaned_data['mobile'])

        return user
