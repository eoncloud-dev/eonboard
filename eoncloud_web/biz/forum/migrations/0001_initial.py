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
            name='Forum',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('content', models.CharField(max_length=500, verbose_name='content')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('status', models.BooleanField(default=False, verbose_name='Close Status')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'forum',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForumReply',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('reply_content', models.CharField(max_length=500, verbose_name='content')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('forum', models.ForeignKey(to='forum.Forum')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_data_center', models.ForeignKey(to='idc.UserDataCenter')),
            ],
            options={
                'db_table': 'forum_reply',
            },
            bases=(models.Model,),
        ),
    ]
