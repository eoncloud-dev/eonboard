#-*-coding-utf-8-*-


from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from biz.account.forms import CloudUserCreateForm
from biz.account.models import Contract, Quota, Operation
from biz.account.serializer import ContractSerializer, OperationSerializer
from biz.account.utils import get_quota_usage

def signup(request, template_name="signup.html"):

    error = None
    if request.method == "GET":
        userCreationForm = CloudUserCreateForm()
    elif request.method == "POST":
        user = User()
        userCreationForm = CloudUserCreateForm(data=request.POST, instance=user)
        if userCreationForm.is_valid():
            userCreationForm.save()
            return HttpResponseRedirect(reverse("signup_success"))

    if userCreationForm.errors.has_key("__all__"):
        error = userCreationForm.errors['__all__']
    else:
        error = userCreationForm.errors



    return render_to_response(template_name, RequestContext(request, {
            "MCC": settings.MCC,
            "SOURCE": settings.SOURCE,
            "USER_TYPE": settings.USER_TYPE,
            "BRAND": settings.BRAND,
            "userCreationForm": userCreationForm,
            "error": error,
    }))


def signup_success(request, template_name="signup_success.html"):
    return render_to_response(template_name, RequestContext(request, {
            "BRAND": settings.BRAND, 
    }))


def find_password(request, template_name="find_password.html"):
    return render_to_response(template_name, RequestContext(request, {
            "BRAND": settings.BRAND, 
    }))


@api_view(["GET"])
def contract_view(request):
    c = Contract.objects.filter(user=request.user, udc__id=request.session["UDC_ID"])[0]
    s = ContractSerializer(c)
    return Response(s.data)


@api_view(["GET"])
def quota_view(request):
    quota = get_quota_usage(request.user, request.session["UDC_ID"])
    return Response(quota)


class OperationList(generics.ListCreateAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    
    def list(self, request):
        try:
            queryset = self.get_queryset().filter(user=request.user,
                            udc__id=request.session["UDC_ID"])
            serializer = OperationSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response()

    def create(self, request, *args, **kwargs):
        raise 
