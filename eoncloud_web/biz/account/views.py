#-*-coding-utf-8-*-

from datetime import datetime
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import check_password


from biz.account.settings import QUOTA_ITEM, NotificationLevel
from biz.account.models import (Contract, Operation, Quota,
                                UserProxy, Notification, Feed)
from biz.account.serializer import (ContractSerializer, OperationSerializer,
                                    UserSerializer, QuotaSerializer, FeedSerializer,
                                    DetailedUserSerializer, NotificationSerializer)
from biz.account.utils import get_quota_usage
from biz.idc.models import DataCenter
from eoncloud_web.pagination import PagePagination
from eoncloud_web.decorators import require_POST, require_GET
from eoncloud_web.shortcuts import retrieve_params

LOG = logging.getLogger(__name__)


@api_view(["GET"])
def contract_view(request):
    c = Contract.objects.filter(user=request.user, udc__id=request.session["UDC_ID"])[0]
    s = ContractSerializer(c)
    return Response(s.data)


@api_view(["GET"])
def quota_view(request):
    quota = get_quota_usage(request.user, request.session["UDC_ID"])
    return Response(quota)


class OperationList(generics.ListAPIView):
    queryset = Operation.objects
    serializer_class = OperationSerializer
    pagination_class = PagePagination

    def get_queryset(self):

        request = self.request
        resource = request.query_params.get('resource')
        resource_name = request.query_params.get('resource_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = super(OperationList, self).get_queryset()

        if resource:
            queryset = queryset.filter(resource=resource)

        if resource_name:
            queryset = queryset.filter(resource_name__istartswith=resource_name)

        if start_date:
            queryset = queryset.filter(create_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(create_date__lte=end_date)

        if request.user.is_superuser:

            data_center_pk = request.query_params.get('data_center', '')
            operator_pk = request.query_params.get('operator', '')

            if data_center_pk:
                queryset = queryset.filter(udc__data_center__pk=data_center_pk)

            if operator_pk:
                queryset = queryset.filter(user__pk=operator_pk)
        else:
            queryset = queryset.filter(user=request.user, udc__id=request.session["UDC_ID"])

        return queryset.order_by('-create_date')


@api_view()
def operation_filters(request):
    resources = Operation.objects.values('resource').distinct()

    for data in resources:
        data['name'] = _(data['resource'])

    return Response({
        "resources": resources,
        "operators": UserProxy.normal_users.values('pk', 'username'),
        "data_centers": DataCenter.objects.values('pk', 'name')
    })


class ContractList(generics.ListCreateAPIView):
    queryset = Contract.living.filter(deleted=False)
    serializer_class = ContractSerializer

    def list(self, request, *args, **kwargs):
        serializer = ContractSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ContractDetail(generics.RetrieveAPIView):
    queryset = Contract.living.all()
    serializer_class = ContractSerializer


@api_view(['POST'])
def create_contract(request):
    try:
        serializer = ContractSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            contract = serializer.save()
            Operation.log(contract, contract.name, 'create', udc=contract.udc, user=request.user)

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
        Operation.log(contract, contract.name, 'update', udc=contract.udc, user=request.user)

        return Response({'success': True, "msg": _('Contract is updated successfully!')},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update contract for unknown reason.')})


@api_view(['POST'])
def delete_contracts(request):
    try:

        contract_ids = request.data.getlist('contract_ids[]')

        for contract_id in contract_ids:
            contract = Contract.objects.get(pk=contract_id)
            contract.deleted = True
            contract.save()
            Quota.living.filter(contract__pk=contract_id).update(deleted=True, update_date=timezone.now())

            Operation.log(contract, contract.name, 'delete', udc=contract.udc, user=request.user)

        return Response({'success': True, "msg": _('Contracts have been deleted!')}, status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to delete contracts, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to delete contracts for unknown reason.')})


class UserList(generics.ListAPIView):
    queryset = UserProxy.normal_users
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data)


@require_GET
def active_users(request):
    queryset = UserProxy.normal_users.filter(is_active=True)
    serializer = UserSerializer(queryset.all(), many=True)
    return Response(serializer.data)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProxy.normal_users.all()
    serializer_class = DetailedUserSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(['POST'])
def deactivate_user(request):
    pk = request.data['id']

    user = User.objects.get(pk=pk)
    user.is_active = False
    user.save()

    return Response({"success": True, "msg": _('User has been deactivated!')}, status=status.HTTP_200_OK)


@api_view(['POST'])
def activate_user(request):
    pk = request.data['id']

    user = User.objects.get(pk=pk)
    user.is_active = True
    user.save()

    return Response({"success": True, "msg": _('User has been activated!')}, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_password(request):

    user = request.user
    old_password = request.data['old_password']
    new_password = request.data['new_password']
    confirm_password = request.data['confirm_password']

    if new_password != confirm_password:
        return Response({"success": False, "msg": _("The new password doesn't match confirm password!")})

    if not check_password(old_password, user.password):
        return Response({"success": False, "msg": _("The original password is not correct!")})

    user.set_password(new_password)
    user.save()

    return Response({"success": True, "msg": _("Password has been changed! Please login in again.")})


class QuotaList(generics.ListAPIView):
    queryset = Quota.living
    serializer_class = QuotaSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if 'contract_id' in request.query_params:
            queryset = queryset.filter(contract__id=request.query_params['contract_id'])

        return Response(self.serializer_class(queryset, many=True).data)


class QuotaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quota.living
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

            if quota_id and Quota.living.filter(contract=contract, pk=quota_id).exists():
                Quota.objects.filter(pk=quota_id).update(resource=resource,
                                                         limit=limit,
                                                         update_date=timezone.now())
            else:
                Quota.objects.create(resource=resource, limit=limit, contract=contract)

        Operation.log(contract, contract.name + " quota", 'update',
                      udc=contract.udc, user=request.user)

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
        LOG.error("Failed to save quota, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to save quota for unknown reason.')})


@api_view(['POST'])
def delete_quota(request):
    try:
        Quota.living.filter(pk=request.data['id']).update(deleted=True)

        return Response({'success': True,
                         "msg": _('Quota have been deleted successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to create quota, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create quota for unknown reason.')})


@api_view(["GET"])
def get_config_view(request):
    return Response(settings.SITE_CONFIG)


@require_GET
def notification_options(request):
    return Response(NotificationLevel.OPTIONS)


@require_POST
def broadcast(request):
    receiver_ids = request.data.getlist('receiver_ids[]')
    level, title, content = retrieve_params(request.data,
                                            'level', 'title', 'content')

    receivers = UserProxy.normal_users.filter(is_active=True)
    if receiver_ids:
        receivers = UserProxy.normal_users.filter(pk__in=receiver_ids)

    Notification.broadcast(receivers, title, content, level)

    return Response({"success": True,
                     "msg": _('Notification is sent successfully!')})


@require_POST
def data_center_broadcast(request):

    dc_id, level, title, content = retrieve_params(
        request.data, 'data_center', 'level', 'title', 'content')

    receivers = UserProxy.normal_users.filter(
        userdatacenter__data_center__pk=dc_id, is_active=True)

    Notification.broadcast(receivers, title, content, level)

    return Response({"success": True,
                     "msg": _('Notification is sent successfully!')})


@require_POST
def announce(request):
    level, title, content = retrieve_params(request.data, 'level', 'title', 'content')
    Notification.objects.create(title=title, content=content, level=level, is_announcement=True)

    return Response({"success": True,
                     "msg": _('Announcement is sent successfully!')})


class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_auto=False).order_by('-create_date')
        return Response(self.serializer_class(queryset, many=True).data)


class NotificationDetail(generics.RetrieveDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class FeedList(generics.ListAPIView):
    queryset = Feed.living.all()
    serializer_class = FeedSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(receiver=request.user).order_by('-create_date')
        return Response(self.serializer_class(queryset, many=True).data)


class FeedDetail(generics.RetrieveDestroyAPIView):
    queryset = Feed.living.all()
    serializer_class = FeedSerializer

    def perform_destroy(self, instance):
        instance.fake_delete()


@require_GET
def feed_status(request):
    Notification.pull_announcements(request.user)
    num = Feed.living.filter(receiver=request.user, is_read=False).count()
    return Response({"num": num})


@require_POST
def mark_read(request, pk):
    Feed.living.get(pk=pk).mark_read()
    return Response(status=status.HTTP_200_OK)


@require_POST
def initialize_user(request):

    user_id = request.data['user_id']
    user = User.objects.get(pk=user_id)
    link_user_to_dc_task(user, DataCenter.get_default())

    return Response({"success": True,
                     "msg": _("Initialization is successful.")})
