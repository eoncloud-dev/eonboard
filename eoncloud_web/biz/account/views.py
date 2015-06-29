#-*-coding-utf-8-*-

from datetime import datetime
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from biz.account.forms import CloudUserCreateForm
from biz.account.models import Contract, Operation
from biz.account.serializer import ContractSerializer, OperationSerializer, UserSerializer
from biz.account.utils import get_quota_usage

LOG = logging.getLogger(__name__)


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


@api_view(["GET"])
def summary(request):
    return Response({"num": User.objects.count()})


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


class ContractList(generics.ListCreateAPIView):
    queryset = Contract.objects.filter(deleted=False)
    serializer_class = ContractSerializer

    def list(self, request):
        serializer = ContractSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ContractDetail(generics.RetrieveAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


@api_view(['POST'])
def create_contract(request):
    try:
        serializer = ContractSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Create contract success!')}, status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Data valid error'), 'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("create contract  error, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Contract create error')})


@api_view(['POST'])
def update_contract(request):
    try:

        pk = request.data['id']

        contract = Contract.objects.get(pk=pk)

        contract.name = request.data['name']

        contract.customer = request.data['customer']

        contract.start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d %H:%M:%S')

        contract.end_date = datetime.strptime(request.data['end_date'], '%Y-%m-%d %H:%M:%S')

        contract.save()

        return Response({'success': True, "msg": _('Create contract success!')}, status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("create contract  error, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Contract create error')})


@api_view(['POST'])
def delete_contracts(request):
    try:

        contract_ids = request.data.getlist('contract_ids[]')

        Contract.objects.filter(pk__in=contract_ids).update(deleted=True)

        return Response({'success': True, "msg": _('Delete contracts success!')}, status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("create contract  error, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Contract create error')})


class UserList(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
