# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volume', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volume',
            name='status',
            field=models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Volume Creating'), (1, 'Volume Attaching'), (2, 'Volume Available'), (3, 'Volume Backing Up'), (4, 'Volume Deleting'), (5, 'Volume Downloading'), (6, 'Volume Error'), (7, 'Volume Error Deleting'), (8, 'Volume Error Restoring'), (9, 'Volume In Use'), (10, 'Volume Restoring Backup'), (12, 'Volume Unrecognized'), (11, 'Volume Uploading'), (13, 'Applying'), (14, 'Rejected')]),
            preserve_default=True,
        ),
    ]
