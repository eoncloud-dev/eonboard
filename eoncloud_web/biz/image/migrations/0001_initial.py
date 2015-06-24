# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('idc', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Image Name')),
                ('uuid', models.CharField(help_text='Openstack Image UUID', max_length=255, verbose_name='UUID')),
                ('login_name', models.CharField(max_length=255, verbose_name='Login Name')),
                ('os_type', models.PositiveIntegerField(verbose_name='Image OS Type', choices=[(1, 'Windows'), (2, 'Linux')])),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('data_center', models.ForeignKey(to='idc.DataCenter')),
                ('user', models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'db_table': 'image',
                'verbose_name': 'Image',
                'verbose_name_plural': 'Image',
            },
            bases=(models.Model,),
        ),
    ]
