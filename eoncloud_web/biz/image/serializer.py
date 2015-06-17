#-*-coding-utf-8-*-

from django.contrib.auth.models import User
from rest_framework import serializers


from biz.image.models import Image


class ImageSerializer(serializers.ModelSerializer):
    os_type = serializers.SerializerMethodField("get_type_slug")
    class Meta:
        model = Image

    def get_type_slug(self, obj):
        slug_dict = {1: 'Windows', 2: 'Linux'}
        return slug_dict[obj.os_type]
