#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

import logging
from smtplib import SMTPException

from django.core.mail import send_mail as _send_mail

from celery import app

LOG = logging.getLogger("cloud.tasks.notify")


@app.task
def send_mail(subject, message, from_email,
              recipient, html_message=None):
    try:
        return _send_mail(subject, message, from_email,
                          [recipient], html_message=html_message)

    except SMTPException as e:
        LOG.exception("Failed to send email", e)
