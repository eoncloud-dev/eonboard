#-*-coding-utf-8-*-
from django.contrib.auth.models import User

from rest_framework import serializers
from biz.idc.models import UserDataCenter

from biz.network.models import Network,Subnet,Router, RouterInterface


class NetworkSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    address = serializers.CharField(source="net_address", required=False, allow_null=True, default=None, read_only=True)
    router_info = serializers.CharField(source="router", required=False, allow_null=True, default=None, read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = Network


class SubnetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    network_info = NetworkSerializer(source="network", required=False, allow_null=True, default=None, read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = Subnet


class RouterSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = Router


class RouterInterfaceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    class Meta:
        model = RouterInterface
