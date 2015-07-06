#-*-coding-utf-8-*-

from rest_framework import serializers


from biz.image.models import Image


class ImageSerializer(serializers.ModelSerializer):

    disk_size = serializers.ReadOnlyField()
    data_center_name = serializers.ReadOnlyField()
    owner_name = serializers.ReadOnlyField()
    os_name = serializers.ReadOnlyField()

    class Meta:
        model = Image
