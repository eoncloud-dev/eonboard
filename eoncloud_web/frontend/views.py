#-*- coding=utf-8 -*-

import logging

from django.conf import settings
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import (HttpResponseRedirect,
                         JsonResponse,
                         HttpResponseForbidden)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context

from biz.account.models import Notification, ActivateUrl
from frontend.forms import CloudUserCreateForm
from biz.idc.models import DataCenter, UserDataCenter as UDC
from biz.workflow.models import Step
from biz.common.decorators import superuser_required
from cloud.tasks import link_user_to_dc_task, send_mail

LOG = logging.getLogger(__name__)


@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('management')
    else:
        return  redirect("cloud")


@login_required
def cloud(request):
    return render(request, "cloud.html")


@superuser_required
def management(request):
    return render(request, 'management.html',
                  {'inited': DataCenter.objects.exists()})


@login_required
def switch_idc(request, dc_id):
    try:
        dc = DataCenter.objects.get(pk=dc_id)

        udc_query = UDC.objects.filter(data_center=dc, user=request.user)

        if not udc_query.exists():
            link_user_to_dc_task(request.user, dc)

        request.session["UDC_ID"] = udc_query[0].id

    except Exception as ex:
        LOG.exception(ex)

    return HttpResponseRedirect(reverse("cloud"))


class LoginView(View):

    def get(self, request):
        return self.response(request)

    def post(self, request):
        form = AuthenticationForm(data=request.POST)

        if not form.is_valid():
            return self.response(request, form)

        user = form.get_user()

        auth_login(request, user)

        if user.is_superuser:
            return redirect('management')

        udc_set = UDC.objects.filter(user=user)

        if udc_set.exists():
            request.session["UDC_ID"] = udc_set[0].id
        else:
            return redirect('no_udc')

        Notification.pull_announcements(user)

        return HttpResponseRedirect(reverse("cloud"))

    def response(self, request, form=None):

        if form is None:
            form = AuthenticationForm(initial={'username': ''})
            error = False
        else:
            error = True

        return render(request, 'login.html', {
            "form": form,
            "error": error
        })


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("index"))


def current_user(request):
    if request.user.is_authenticated():

        if request.user.is_superuser:
            return JsonResponse({'result': {'logged': True}, 'user': request.user.username})

        udc_id = request.session["UDC_ID"]
        data_center_names = DataCenter.objects.filter(userdatacenter__pk=udc_id)
        cc_name = data_center_names[0].name if data_center_names else u'N/A'
        is_approver = Step.objects.filter(approver__pk=request.user.pk).exists()

        return JsonResponse({'result': {'logged': True},
                            'user': request.user.username,
                            'datacenter': cc_name,
                            'is_approver': is_approver})
    else:
        return JsonResponse({'result': {'logged': False}})


class SignupView(View):

    def get(self, request):
        return self.response(request, CloudUserCreateForm(
            initial={'username': '',  'email': '', 'mobile': ''}))

    def post(self, request):

        user = User()
        form = CloudUserCreateForm(data=request.POST, instance=user)

        if form.is_valid():
            form.save()

            if settings.REGISTER_ACTIVATE_EMAIL_ENABLED:
                _send_activate_email(user)
                msg = _("Your registration successed, we send you one "
                        "activate email, please check your input box.")
            else:
                link_user_to_dc_task.delay(user, DataCenter.get_default())
                msg = _("Your registration successed!")

            return render(request, 'info.html', {'message': msg})

        return self.response(request, form, form.errors)

    def response(self, request, form, errors=None):

        context = {
            "MCC": settings.MCC,
            "SOURCE": settings.SOURCE,
            "USER_TYPE": settings.USER_TYPE,
            "BRAND": settings.BRAND,
            "form": form,
            "errors": errors,
        }

        return render(request, 'signup.html', context)

    def dispatch(self, request, *args, **kwargs):

        if settings.SIGNUP_ENABLED:
            return super(SignupView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


signup = SignupView.as_view()


def first_activate_user(request, code):

    try:
        activate_url = ActivateUrl.objects.get(code=code)
    except ActivateUrl.DoesNotExist:
        return _resend_email_response(request,
                                      _("This activate url is not valid, "
                                        "you can resend activate email."))

    if activate_url.expire_date < timezone.now():
        activate_url.delete()
        return _resend_email_response(request,
                                      _("This activate url is not valid, "
                                        "you can resend activate email."))

    try:
        link_user_to_dc_task(activate_url.user, DataCenter.get_default())
    except:
        return render(request, 'info.html', {
            'message': _("Failed to activate your account, you can try later.")
        })
    else:
        activate_url.delete()
        messages.add_message(request, messages.INFO,
                             _("Your account is activated successfully, "
                               "please login."))
        return redirect('login')


def resend_activate_email(request):

    username = request.POST['username']
    password = request.POST['password']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return _resend_email_response(request, _("No account found."))

    if not user.check_password(password):
        return _resend_email_response(request, _("Password is not correct."))

    _send_activate_email(user)

    return render(request, 'info.html', {
        'message': _("Your activate email is sent, "
                     "please check your input box.")
    })


def _resend_email_response(request, error):
    return render(request, 'resend_activate_email.html', {'error': error})


def find_password(request):
    return render(request, 'find_password.html')


@login_required
def no_udc(request):

    login_via_ldap = hasattr(request.user, 'ldap_user')

    return render(request, 'no_udc.html', {
        "login_via_ldap": login_via_ldap
    })


def _send_activate_email(user):
    template = get_template('signup_activate_email.html')
    activate_url = ActivateUrl.generate(user)
    context = Context({
        'user': user,
        'url': activate_url.url,
        'BRAND': settings.BRAND,
        'EXTERNAL_URL': settings.EXTERNAL_URL})

    html = template.render(context)

    subject = _("%(site_name)s - Activate Account") \
        % {'site_name': settings.BRAND}

    sender = "%(site_name)s <%(email)s>" \
             % {'site_name': settings.BRAND,
                'email': settings.DEFAULT_FROM_EMAIL}

    send_mail.delay(subject, '',
                    sender,
                    user.email, html_message=html)