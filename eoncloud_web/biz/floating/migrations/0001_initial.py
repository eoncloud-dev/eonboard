# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Floating',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('ip', models.CharField(max_length=255, null=True, verbose_name='Public IP', blank=True)),
                ('uuid', models.CharField(max_length=128, null=True, verbose_name=b'Floating uuid', blank=True)),
                ('fixed_ip', models.CharField(max_length=128, null=True, verbose_name=b'Fixed IP', blank=True)),
                ('port_id', models.CharField(max_length=128, null=True, verbose_name=b'Port uuid', blank=True)),
                ('status', models.IntegerField(default=10, verbose_name='Status', choices=[(0, 'Floating ERROR'), (1, 'Floating Allocate'), (10, 'Floating Avaiable'), (20, 'Floating Binded'), (21, 'Floating Binding'), (90, 'Floating Released'), (91, 'Floating Releasing')])),
                ('bandwidth', models.IntegerField(default=2, verbose_name='Bandwidth MB')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('delete_date', models.DateTimeField(null=True, verbose_name='Delete Date', blank=True)),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('instance', models.ForeignKey(default=None, blank=True, to='instance.Instance', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'floating',
                'verbose_name': 'Floating',
                'verbose_name_plural': 'Floating',
            },
            bases=(models.Model,),
        ),
    ]
