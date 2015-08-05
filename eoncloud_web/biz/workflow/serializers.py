#!/usr/bin/env python
# coding=utf-8

__author__ = 'bluven'


from rest_framework import serializers

from biz.workflow.models import Workflow, Step, FlowInstance


class WorkflowStepSerializer(serializers.ModelSerializer):
    approver_name = serializers.ReadOnlyField()

    class Meta:
        model = Step


class WorkflowSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    update_date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    resource_name = serializers.ReadOnlyField()

    class Meta:
        model = Workflow


class StepInstanceSerializer(serializers.ModelSerializer):
    approver_name = serializers.ReadOnlyField()

    class Meta:
        model = Step


class BasicFlowInstanceSerializer(serializers.ModelSerializer):
    current_step = StepInstanceSerializer(read_only=True)
    steps = StepInstanceSerializer(many=True, read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    update_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    resource_name = serializers.ReadOnlyField()
    resource_info = serializers.ReadOnlyField()

    class Meta:
        model = FlowInstance
        fields = ('id', 'name', 'owner_name', 'current_step', 'steps', 'is_complete', 'reject_reason',
                  'resource_name', 'resource_info', 'create_date', 'update_date')
