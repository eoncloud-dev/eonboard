# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instance', '__first__'),
        ('idc', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Volume name')),
                ('volume_id', models.CharField(max_length=128, null=True, verbose_name='OS Volume UUID')),
                ('size', models.IntegerField(verbose_name='Volume size')),
                ('volume_type', models.IntegerField(default=0, verbose_name='Volume Type', choices=[(0, 'Capacity'), (1, 'Performance')])),
                ('status', models.IntegerField(default=0, verbose_name='Status', choices=[(0, 'Volume Creating'), (1, 'Volume Attaching'), (2, 'Volume Available'), (3, 'Volume Backing_up'), (4, 'Volume Deleting'), (5, 'Volume Downloading'), (6, 'Volume Error'), (7, 'Volume Error_deleting'), (8, 'Volume Error_restoring'), (9, 'Volume In Use'), (10, 'Volume Restoring_backup'), (12, 'Volume Unrecognized'), (11, 'Volume uploading')])),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('instance', models.ForeignKey(blank=True, to='instance.Instance', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'ordering': ['-create_date'],
                'db_table': 'volume',
                'verbose_name': 'Volume',
                'verbose_name_plural': 'Volume',
            },
            bases=(models.Model,),
        ),
    ]
