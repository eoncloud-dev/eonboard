#coding=utf-8

import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view

from biz.image.models import Image
from biz.image.serializer import ImageSerializer

LOG = logging.getLogger(__name__)


class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        if not request.user.is_superuser:
            queryset = queryset.filter(data_center__pk=request.session["UDC_ID"])

        serializer = ImageSerializer(queryset, many=True)

        return Response(serializer.data)


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


@api_view(["POST"])
def create_image(request):
    try:
        serializer = ImageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Image is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Image data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create image, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to create image for unknown reason.')})


@api_view(["POST"])
def update_image(request):
    try:

        image = Image.objects.get(pk=request.data['id'])

        serializer = ImageSerializer(instance=image, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "msg": _('Image is updated successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False, "msg": _('Image data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create image, msg:[%s]" % e)
        return Response({"success": False, "msg": _('Failed to update image for unknown reason.')})


@api_view(["POST"])
def delete_images(request):

    ids = request.data.getlist('ids[]')

    Image.objects.filter(pk__in=ids).delete()

    return Response({'success': True, "msg": _('Images have been deleted!')}, status=status.HTTP_200_OK)
