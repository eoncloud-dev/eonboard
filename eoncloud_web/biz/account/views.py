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
from biz.account.models import Contract, Operation, Quota, QUOTA_ITEM
from biz.account.serializer import ContractSerializer, OperationSerializer, UserSerializer, QuotaSerializer
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
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(user=request.user, udc__id=request.session["UDC_ID"])
            serializer = OperationSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response()

    def create(self, request, *args, **kwargs):
        raise


class ContractList(generics.ListCreateAPIView):
    queryset = Contract.objects.filter(deleted=False)
    serializer_class = ContractSerializer

    def list(self, request, *args, **kwargs):
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
            return Response({'success': True,
                             "msg": _('Contract is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False,
                             "msg": _('Contract data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create contract for unknown reason.')})


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

        return Response({'success': True, "msg": _('Contract is updated successfully!')},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update contract for unknown reason.')})


@api_view(['POST'])
def delete_contracts(request):
    try:

        contract_ids = request.data.getlist('contract_ids[]')

        Contract.objects.filter(pk__in=contract_ids).update(deleted=True)

        return Response({'success': True, "msg": _('Contracts have been deleted!')}, status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to delete contracts, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to delete contracts for unknown reason.')})


class UserList(generics.ListAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class QuotaList(generics.ListAPIView):

    queryset = Quota.objects

    serializer_class = QuotaSerializer

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        if 'contract_id' in request.data:

            queryset = queryset.filter(contract__id=request.data['contract_id'])

        return Response(self.serializer_class(queryset, many=True).data)


class QuotaDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Quota.objects.all()

    serializer_class = QuotaSerializer


@api_view(['GET'])
def resource_options(request):
    return Response(QUOTA_ITEM)


@api_view(['POST'])
def create_quotas(request):
    try:

        contract = Contract.objects.get(pk=request.data['contract_id'])

        quota_ids = request.data.getlist('ids[]')
        resources = request.data.getlist('resources[]')
        limits = request.data.getlist('limits[]')

        for index, quota_id in enumerate(quota_ids):

            resource, limit = resources[index], limits[index]

            if quota_id and Quota.objects.filter(contract=contract, pk=quota_id, deleted=False).exists():
                Quota.objects.filter(pk=quota_id).update(resource=resource, limit=limit)
            else:
                Quota.objects.create(resource=resource, limit=limit, contract=contract)

        return Response({'success': True,
                         "msg": _('Quotas have been saved successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to save quotas, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to save quotas for unknown reason.')})


@api_view(['POST'])
def create_quota(request):
    try:

        contract = Contract.objects.get(pk=request.data['contract'])

        resource, limit = request.data['resource'], request.data['limit']

        pk = request.data['id'] if 'id' in request.data else None

        if pk and Quota.objects.filter(pk=pk).exists():

            quota = Quota.objects.get(pk=pk)

            quota.limit = limit

            quota.save()

        else:
            quota = Quota.objects.create(resource=resource, limit=limit, contract=contract)

        return Response({'success': True,
                         "msg": _('Quota have been saved successfully!'),
                         "quota": QuotaSerializer(quota).data},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        print e
        LOG.error("Failed to save quota, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to save quota for unknown reason.')})


@api_view(['POST'])
def delete_quota(request):
    try:

        Quota.objects.filter(pk=request.data['id']).update(deleted=True)

        return Response({'success': True,
                         "msg": _('Quota have been deleted successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to create quota, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create quota for unknown reason.')})
