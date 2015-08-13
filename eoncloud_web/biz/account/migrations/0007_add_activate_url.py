# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0006_notification_is_auto'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivateUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=128)),
                ('expire_date', models.DateTimeField()),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'activate_url',
                'verbose_name': 'Activate Url',
                'verbose_name_plural': 'Activate Urls',
            },
            bases=(models.Model,),
        ),
    ]
