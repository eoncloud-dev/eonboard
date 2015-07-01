#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'


from django.db import models


class LivingManager(models.Manager):

    def get_queryset(self):
        return super(LivingManager, self).get_queryset().filter(deleted=False)


class DeletedManager(models.Manager):

    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(deleted=True)


class LivingDeadModel(models.Model):

    class Meta:
        abstract = True

    objects = models.Manager()

    living = LivingManager()

    dead = DeletedManager()
