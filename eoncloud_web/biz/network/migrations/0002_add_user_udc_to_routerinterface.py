# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='routerinterface',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='routerinterface',
            name='user_data_center',
            field=models.ForeignKey(default=None, to='idc.UserDataCenter', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='router',
            name='is_gateway',
            field=models.BooleanField(default=False, verbose_name='Whether to open the gateway'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='routerinterface',
            name='network_id',
            field=models.IntegerField(null=True, verbose_name='Network', blank=True),
            preserve_default=True,
        ),
    ]
