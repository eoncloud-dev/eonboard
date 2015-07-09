# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forum',
            old_name='status',
            new_name='closed',
        ),
        migrations.RemoveField(
            model_name='forumreply',
            name='user_data_center',
        ),
    ]
