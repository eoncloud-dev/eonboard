#coding=utf-8

from rest_framework import serializers

from django.contrib.auth.models import User

from biz.account.models import Contract, Quota, Operation, UserProxy, Notification, NOTIFICATION_KEY_METHODS

from biz.idc.serializer import DetailedUserDataCenterSerializer


class ContractSerializer(serializers.ModelSerializer):
    quotas = serializers.ReadOnlyField(source="get_quotas")
    start_date = serializers.DateTimeField(format="%Y-%m-%d", required=False, allow_null=True)
    end_date = serializers.DateTimeField(format="%Y-%m-%d", required=False, allow_null=True)

    username = serializers.ReadOnlyField(source="user.username")
    tenant_name = serializers.ReadOnlyField(source="udc.tenant_name")

    class Meta:
        model = Contract


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota


class OperationSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    desc = serializers.ReadOnlyField(source="get_desc")
    resource_i18n = serializers.ReadOnlyField(source="get_resource")
    operator = serializers.ReadOnlyField()
    data_center_name = serializers.ReadOnlyField()

    class Meta:
        model = Operation


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User


class DetailedUserSerializer(serializers.ModelSerializer):
    user_data_centers = DetailedUserDataCenterSerializer(read_only=True, many=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = UserProxy


class NotificationSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    is_info = serializers.ReadOnlyField()
    is_success = serializers.ReadOnlyField()
    is_error = serializers.ReadOnlyField()
    is_warning = serializers.ReadOnlyField()
    is_danger = serializers.ReadOnlyField()
    time_ago = serializers.ReadOnlyField()

    class Meta:
        model = Notification

