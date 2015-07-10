#-*-coding-utf-8-*-

from django.contrib.auth.models import User
from rest_framework import serializers

from biz.idc.models import UserDataCenter
from biz.floating.models import Floating
from biz.instance.serializer import InstanceSerializer


class FloatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)

    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)
    delete_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)

    resource_info = serializers.DictField(source="re_resource", read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"]) 

    class Meta:
        model = Floating


