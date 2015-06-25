#-*-coding=utf-8-*-


import json

from django.conf import settings
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from biz.idc.models import UserDataCenter as UDC


def index(request, template_name="index.html"):
    return render_to_response(template_name, RequestContext(request, {}))


@login_required
def cloud(request, template_name="cloud.html"):
    return render_to_response(template_name, RequestContext(request, {
    }))


@login_required
def management(request):
    return render(request, 'management.html')


def login(request, template_name="login.html"):

    if request.method == "GET":
        authenticationForm = AuthenticationForm()
    elif request.method == "POST":
        authenticationForm = AuthenticationForm(data=request.POST)
        if authenticationForm.is_valid():
            user = authenticationForm.get_user()

            auth_login(request, user)

            if user.is_superuser:
                return redirect('management')

            ucc = UDC.objects.filter(user=user)
            if ucc:
                request.session["UDC_ID"] = ucc[0].id
            else:
                raise Exception("User has not register to any SDDC")
            return HttpResponseRedirect(reverse("cloud"))

    # if authenticationForm.errors.has_key("__all__"):
    #     error = authenticationForm.errors['__all__']

    return render_to_response(template_name, RequestContext(request, {
        "authenticationForm": authenticationForm,
        "error": authenticationForm.errors.get('__all__', None),
        "BRAND": settings.BRAND,
    }))



def logout(request):
    auth_logout(request) 
    return HttpResponseRedirect(reverse("index"))


def current_user(request):
    if request.user.is_authenticated():
        ucc_id = request.session["UDC_ID"]
        ucc = UDC.objects.filter(pk=ucc_id)
        cc_name = ""
        if ucc and len(ucc) == 1:
            cc_name = ucc[0].data_center.name;
        return HttpResponse(json.dumps({
                            'result': {'logged': True},
                            'user': request.user.username,
                            'datacenter': cc_name}),
                        content_type="application/json")
    else:
        return HttpResponse(json.dumps({'result': {'logged': False}}), 
                            content_type="application/json") 
