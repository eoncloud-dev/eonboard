# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volume', '0002_change_status_set_of_volume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volume',
            name='status',
            field=models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Creating'), (1, 'Attaching'), (2, 'Available'), (3, 'Backing Up'), (4, 'Deleting'), (5, 'Downloading'), (6, 'Error'), (7, 'Delete Failure'), (8, 'Restore Failure'), (9, 'In Use'), (10, 'Restoring Backup'), (12, 'Unrecognized'), (11, 'Uploading'), (13, 'Applying'), (14, 'Rejected'), (15, 'Detaching')]),
            preserve_default=True,
        ),
    ]
