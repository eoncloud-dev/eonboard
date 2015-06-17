#-*-coding-utf-8-*-
from django.contrib.auth.models import User
from rest_framework import serializers

from biz.idc.models import UserDataCenter
from biz.volume.models import Volume
from biz.instance.serializer import InstanceSerializer


class VolumeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True, default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(queryset=UserDataCenter.objects.all(), required=False, allow_null=True, default=None)
    instance_info = InstanceSerializer(source="instance", required=False, allow_null=True, default=None, read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False, allow_null=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
            model = Volume
