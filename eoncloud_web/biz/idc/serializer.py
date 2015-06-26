#!/usr/bin/env python
# coding=utf-8

from rest_framework import serializers

from biz.idc.models import UserDataCenter


class UserDataCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDataCenter