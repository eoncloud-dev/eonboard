#-*-coding=utf-8-*-

from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eoncloud_web.settings')
from django.conf import settings

app = Celery('cloud',
             broker=settings.BROKER_URL,
             backend='amqp',
             include=['cloud.tasks'])

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_RESULT_PERSISTENT=True,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'],
)
