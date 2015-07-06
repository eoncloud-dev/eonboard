# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('account', '0002_delete_contract_user_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='contract',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Create Date', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now=True, auto_now_add=True, verbose_name='Update Date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quota',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now=True, auto_now_add=True, verbose_name='Update Date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contract',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='operation',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='operation',
            name='resource',
            field=models.CharField(max_length=128, verbose_name='Resource'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='quota',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Create Date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='quota',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
    ]
