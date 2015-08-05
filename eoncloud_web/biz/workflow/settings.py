#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from django.utils.translation import ugettext_lazy as _

from biz.instance.models import Instance
from biz.floating.models import Floating
from biz.volume.models import Volume


class ResourceType(object):

    INSTANCE = 'instance'

    FLOATING = 'floating'

    VOLUME = 'volume'

    NAME_MAP = {
        INSTANCE: _("Instance"),
        FLOATING: _("Floating IP"),
        VOLUME: _("Volume"),
    }

    MODEL_MAP = {
        INSTANCE: Instance,
        FLOATING: Floating,
        VOLUME: Volume
    }

    @classmethod
    def get_label(cls, key):
        return cls.NAME_MAP[key]

    @classmethod
    def get_model(cls, key):
        return cls.MODEL_MAP[key]
