# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_refactor_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_auto',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
