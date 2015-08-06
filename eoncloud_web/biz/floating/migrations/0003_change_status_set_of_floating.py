# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('floating', '0002_add_resource_and_resource_type_filed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floating',
            name='status',
            field=models.IntegerField(default=10, verbose_name='Status', choices=[(0, 'Floating ERROR'), (1, 'Floating Allocate'), (2, 'Applying'), (3, 'Rejected'), (10, 'Floating Avaiable'), (20, 'Floating Binded'), (21, 'Floating Binding'), (90, 'Floating Released'), (91, 'Floating Releasing'), (91, 'Floating Releasing')]),
            preserve_default=True,
        ),
    ]
