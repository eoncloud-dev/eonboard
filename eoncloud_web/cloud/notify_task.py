#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail as _send_mail, send_mass_mail

from celery import app

from biz.account.models import UserProxy, Notification

LOG = logging.getLogger("cloud.tasks")


DEFAULT_SENDER = "%s <%s>" % (settings.BRAND, settings.DEFAULT_FROM_EMAIL)


@app.task
def send_mail(subject, message, recipient,
              from_email=DEFAULT_SENDER, html_message=None):
    try:
        return _send_mail(subject, message, from_email,
                          [recipient], html_message=html_message)
    except SMTPException as e:
        LOG.exception("Failed to send email", e)


@app.task
def send_notifications(title, content, level, receiver_ids):

    receivers = UserProxy.normal_users.filter(is_active=True)
    if receiver_ids:
        receivers = UserProxy.normal_users.filter(pk__in=receiver_ids)

    _broadcast(title, content, level, receivers)


@app.task
def send_notifications_by_data_center(title, content, level, dc_ids):

    receivers = UserProxy.normal_users.filter(
        userdatacenter__data_center__pk__in=dc_ids, is_active=True)

    _broadcast(title, content, level, receivers)


def _broadcast(title, content, level, receivers):

    Notification.broadcast(receivers, title, content, level)

    mails = [(title, content, DEFAULT_SENDER, [receiver.email])
             for receiver in receivers if receiver.email]

    send_mass_mail(mails)

