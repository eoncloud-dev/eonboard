#-coding=utf-8-*-

import logging
import time
import traceback
import random

from django.conf import settings

from celery import app
from biz.account.models  import Operation

LOG = logging.getLogger("cloud.tasks")

@app.task
 def operation_save(user, datacenter, **kwargs):
    pass
 

