# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('floating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='floating',
            name='resource',
            field=models.IntegerField(default=None, null=True, verbose_name='Resource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='floating',
            name='resource_type',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='reource type', choices=[(b'INSTANCE', b'INSTANCE'), (b'LOADBALANCER', b'LOADBALANCER')]),
            preserve_default=True,
        ),
    ]
