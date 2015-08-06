# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='status',
            field=models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Instance Waiting'), (1, 'Instance Running'), (2, 'Instance Booting'), (3, 'Instance Rebooting'), (4, 'Instance Paused'), (5, 'Instance Power Off'), (6, 'Instance Shutting Down'), (7, 'Instance Deploying'), (8, 'Instance Deploy Failed'), (9, 'Instance Locked'), (10, 'Instance Delete'), (11, 'Instance Error'), (12, 'Instance Backuping'), (13, 'Instance Restoring'), (14, 'Instance Resizing'), (15, 'Instance Expired'), (16, 'Instance Deleting'), (17, 'Applying'), (18, 'Rejected')]),
            preserve_default=True,
        ),
    ]
