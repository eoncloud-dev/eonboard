# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('object_id', models.PositiveIntegerField()),
                ('reject_reason', models.CharField(max_length=256, verbose_name='Reject Reason')),
                ('is_complete', models.BooleanField(default=False, verbose_name='Completed')),
                ('extra_data', models.TextField(null=True, verbose_name='Extra Data')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'db_table': 'workflow_instance',
                'verbose_name': 'Workflow Instance',
                'verbose_name_plural': 'Workflow Instances',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Step Name')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Step No.')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('approver', models.ForeignKey(related_name='+', verbose_name='Auditor', to=settings.AUTH_USER_MODEL)),
                ('next', models.OneToOneField(related_query_name=b'previous', related_name='previous', null=True, to='workflow.Step')),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'workflow_step',
                'verbose_name': 'Workflow Step',
                'verbose_name_plural': 'Workflow Steps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StepInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Step Name')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Step No.')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('approver', models.ForeignKey(related_name='+', verbose_name='Auditor', to=settings.AUTH_USER_MODEL)),
                ('next', models.OneToOneField(related_query_name=b'previous', related_name='previous', null=True, to='workflow.StepInstance')),
                ('workflow', models.ForeignKey(related_query_name=b'step', related_name='step_set', db_constraint=False, verbose_name='Work Flow', to='workflow.FlowInstance')),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'workflow_step_instance',
                'verbose_name': 'Workflow Step',
                'verbose_name_plural': 'Workflow Steps',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Flow Name')),
                ('resource_type', models.CharField(max_length=30)),
                ('is_default', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
                'db_table': 'workflow',
                'verbose_name': 'Workflow',
                'verbose_name_plural': 'Workflow',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='step',
            name='workflow',
            field=models.ForeignKey(related_query_name=b'step', related_name='steps', verbose_name='Work Flow', to='workflow.Workflow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowinstance',
            name='current_step',
            field=models.ForeignKey(related_name='+', db_constraint=False, verbose_name='Current Step', to='workflow.StepInstance', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowinstance',
            name='owner',
            field=models.ForeignKey(related_query_name=b'process', related_name='process_list', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowinstance',
            name='workflow',
            field=models.ForeignKey(verbose_name='Work Flow', to='workflow.Workflow'),
            preserve_default=True,
        ),
    ]
