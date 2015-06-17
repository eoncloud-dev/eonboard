#coding=utf-8

from rest_framework.response import Response

from biz.idc.models import UserDataCenter
from biz.image.models import Image
from biz.image.serializer import ImageSerializer
from rest_framework import generics


class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def list(self, request):
        udc = UserDataCenter.objects.get(pk=request.session["UDC_ID"])
        queryset = self.get_queryset().filter(data_center=udc.data_center)
        serializer = ImageSerializer(queryset, many=True)
        return Response(serializer.data)


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
