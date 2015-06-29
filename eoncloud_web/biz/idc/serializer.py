#!/usr/bin/env python
# coding=utf-8

from rest_framework import serializers

from biz.idc.models import DataCenter, UserDataCenter


class DataCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataCenter


class UserDataCenterSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDataCenter