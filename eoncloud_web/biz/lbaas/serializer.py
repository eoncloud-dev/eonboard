#-*-coding-utf-8-*-
from django.contrib.auth.models import User
from rest_framework import serializers

from biz.idc.models import UserDataCenter
from biz.lbaas.models import BalancerPool, BalancerVIP, BalancerMember, BalancerMonitor
from biz.lbaas.settings import PROTOCOL_CHOICES, LB_METHOD_CHOICES
from biz.network.serializer import SubnetSerializer
from biz.instance.serializer import InstanceSerializer


class BalancerVIPSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    protocol_desc = serializers.CharField(source='get_protocol_display', read_only=True)
    session_persistence_desc = serializers.CharField(source='get_session_persistence_display', read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = BalancerVIP


class BalancerPoolSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    subnet_info = SubnetSerializer(source="subnet", required=False, allow_null=True, default=None, read_only=True)
    vip_info = BalancerVIPSerializer(source="vip", required=False, allow_null=True, default=None, read_only=True)
    protocol_desc = serializers.CharField(source='get_protocol_display', read_only=True)
    lb_method_desc = serializers.CharField(source='get_lb_method_display', read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
            model = BalancerPool





class BalancerMemberSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)

    instance_info = InstanceSerializer(source="instance", required=False, allow_null=True, default=None, read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = BalancerMember


class BalancerMonitorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    monitor_type_desc = serializers.CharField(source='get_type_display', read_only=True)
    balancer_desc = serializers.CharField(source="balancer", required=False, allow_null=True, default=None, read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = BalancerMonitor
