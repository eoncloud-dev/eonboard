from django.shortcuts import render

# Create your views here.


from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view

from biz.account.models import Contract
from biz.idc.models import DataCenter
from biz.instance.models import Instance, Flavor
from biz.image.models import Image


@api_view(["GET"])
def summary(request):
    return Response({"user_num": User.objects.filter(is_superuser=False).count(),
                     "instance_num": Instance.objects.filter(deleted=False).count(),
                     "flavor_num": Flavor.objects.count(),
                     "data_center_num": DataCenter.objects.count(),
                     "contract_num": Contract.objects.filter(deleted=False).count(),
                     "image_num": Image.objects.count()})
