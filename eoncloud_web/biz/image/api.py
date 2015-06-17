#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from common.product import utils


@api_view(['GET'])
def api_get_options(request):
    serializer = utils.get_product_serializer(request)
    return Response(serializer.data)


@api_view(['GET'])
def api_get_price_unit(request):
    serializer = utils.get_price_unit_serializer(request)
    return Response(serializer.data)


@api_view(['GET'])
def api_get_discount(request):
    return Response(utils.get_discount_data())


@api_view(['GET'])
def api_resize_options(request, instance_id):
    """
    获取Instance升级时，可以选择的各个选项，返回的选项肯定高于当前Instance的配置
    """
    serializer = utils.get_resize_options(instance_id)
    return Response(serializer.data)

