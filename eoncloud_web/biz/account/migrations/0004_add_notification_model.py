# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0003_add_user_proxy_model_and_alter_quota_resource_and_add_create_update_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.IntegerField(default=1, choices=[(1, 'Information'), (2, 'Success'), (3, 'Error'), (4, 'Warning'), (5, 'Danger')])),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('read_date', models.DateTimeField(null=True)),
                ('receiver', models.ForeignKey(related_query_name=b'notification', related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notification',
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='operation',
            options={'verbose_name': 'Operation', 'verbose_name_plural': 'Operation'},
        ),
    ]
