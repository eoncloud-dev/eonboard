#-*-coding-utf-8-*-

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from biz.idc.models import UserDataCenter
from biz.image.serializer import ImageSerializer
from biz.instance.models import Instance, Flavor


class InstanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False, allow_null=True,
                                              default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(
        queryset=UserDataCenter.objects.all(),  required=False,
        allow_null=True, default=None)
    image_info = ImageSerializer(source="image", required=False,
                                 allow_null=True, default=None, read_only=True)
    floating_info = serializers.CharField(source="floating_ip", required=False,
                                          allow_null=True, default=None,
                                          read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                            required=False, allow_null=True)
    terminate_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                               required=False, allow_null=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"])

    class Meta:
        model = Instance


class FlavorSerializer(serializers.ModelSerializer):
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                            required=False, allow_null=True,
                                            read_only=True)

    class Meta:
        model = Flavor
