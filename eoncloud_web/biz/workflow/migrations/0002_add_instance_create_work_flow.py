#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


def init_instance_creation_workflow(apps, schema_editor):

    ContentType = apps.get_model("contenttypes", "ContentType")
    WorkFlow = apps.get_model("workflow", "workflow")
    instance_type = ContentType.objects.get(app_label="instance", model="instance")

    WorkFlow.objects.create(name=_("Instance Creation"), content_type=instance_type)


def fallback(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    WorkFlow = apps.get_model("workflow", "workflow")
    instance_type = ContentType.objects.get(app_label="instance", model="instance")

    WorkFlow.objects.filter(content_type=instance_type).delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_instance_creation_workflow, fallback),
    ]
