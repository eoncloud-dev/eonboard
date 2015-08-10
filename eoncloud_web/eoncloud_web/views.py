#-*- coding=utf-8 -*-

import logging

from django.conf import settings
from django.views.generic import View
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.utils.translation import ugettext_lazy as _


from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from biz.idc.models import DataCenter, UserDataCenter as UDC


from eoncloud_web.decorators import superuser_required

LOG = logging.getLogger(__name__)


def index(request, template_name="index.html"):
    return render_to_response(template_name, RequestContext(request, {}))


@login_required
def cloud(request, template_name="cloud.html"):
    return render_to_response(template_name, RequestContext(request, {}))


@login_required
def switch_idc(request, dc_id):
    try:
        dc = DataCenter.objects.get(pk=dc_id)
        udc = UDC.objects.filter(data_center=dc,
                                user=request.user)
        if len(udc) < 1:
            from cloud.tasks import link_user_to_dc_task
            u = link_user_to_dc_task(request.user, dc)
        
        udc = UDC.objects.filter(data_center=dc,
                                user=request.user)
        if len(udc) == 1:
            request.session["UDC_ID"] = udc[0].id

    except Exception as ex:
        LOG.exception(ex)

    return HttpResponseRedirect(reverse("cloud"))


@superuser_required
def management(request):
    return render(request, 'management.html', {'inited': DataCenter.objects.exists()})


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

        ucc = UDC.objects.filter(user=user)
        if ucc:
            request.session["UDC_ID"] = ucc[0].id
        else:
            raise Exception("User has not register to any SDDC")

        Notification.pull_announcements(user)

        return HttpResponseRedirect(reverse("cloud"))

    def response(self, request, form=None):

        if form is None:
            form = AuthenticationForm(initial={'username': ''})
            error = False
        else:
            error = True

        return render_to_response('login.html', RequestContext(request, {
            "form": form,
            "error": error,
            "BRAND": settings.BRAND,
            "ICP_NUMBER": settings.ICP_NUMBER,
            
        }))


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
        


        return JsonResponse({'result': {'logged': True},
                            'user': request.user.username,
                            'datacenter': cc_name})
    else:
        return JsonResponse({'result': {'logged': False}})

