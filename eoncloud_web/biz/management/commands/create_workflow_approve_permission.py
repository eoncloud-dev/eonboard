#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

from django.core.management import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        content_type = ContentType.objects.get(app_label="workflow",
                                               model="flowinstance")

        if Permission.objects.filter(content_type=content_type,
                                     codename="approve_workflow"):

            print _(u"Workflow approve permission has already created!")
            return

        Permission.objects.create(name=_("Workflow Approve"),
                                  content_type=content_type,
                                  codename="approve_workflow")
