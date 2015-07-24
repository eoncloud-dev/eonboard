# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0004_add_notification_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_read', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('read_date', models.DateTimeField(null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('notification', models.ForeignKey(related_query_name=b'feed', related_name='feeds', to='account.Notification')),
                ('receiver', models.ForeignKey(related_query_name=b'notification', related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_feed',
                'verbose_name': 'Feed',
                'verbose_name_plural': 'Feeds',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='notification',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='is_read',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='read_date',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='receiver',
        ),
        migrations.AddField(
            model_name='notification',
            name='is_announcement',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
