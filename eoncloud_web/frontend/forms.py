#coding=utf-8

from django.conf import settings

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField, CaptchaTextInput as CaptchaTextInput_

from biz.account.models import UserProfile


class CaptchaTextInput(CaptchaTextInput_):
    def render(self, name, value, attrs=None):
        self.fetch_captcha_store(name, value, attrs)

        self.image_and_audio = '''
        <a class="captcha-refresh">
            <img src="%s" alt="captcha"  class="captcha" style="height: 35px;"/>
        </a>
        ''' % self.image_url()

        return super(CaptchaTextInput_, self) \
            .render(name, self._value, attrs=attrs)


class CloudUserCreateForm(UserCreationForm):
    error_messages = UserCreationForm.error_messages.copy()

    error_messages.update({
        u'duplicate_email': _("A user with that email already exists."),
        u'duplicate_mobile': _("A user with that mobile already exists.")
    })

    email = forms.EmailField(label=_("Email"))
    mobile = forms.CharField(label=_("Mobile"))
    # user_type = forms.IntegerField()
    captcha = CaptchaField(
        label=_("Captcha"),
        widget=CaptchaTextInput(
            attrs={'class': 'form-control placeholder-no-fix input-medium',
                   'style': 'display: inline-block;'}),
        required=settings.CAPTCHA_ENABLED)

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages[u'duplicate_email'],
            code='duplicate_email',
        )

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]

        if not UserProfile.objects.filter(mobile=mobile).exists():
            return mobile

        raise forms.ValidationError(
            self.error_messages[u'duplicate_mobile'],
            code='duplicate_mobile',
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


class CloudUserCreateFormWithoutCapatcha(CloudUserCreateForm):
    # make captcha not required, so that when validate data,
    # captcha field won't work
    captcha = CaptchaField(required=False)
