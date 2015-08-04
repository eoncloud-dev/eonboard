
import logging

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response


from eoncloud_web.decorators import require_GET, require_POST
from biz.workflow.models import Workflow, Step, FlowInstance
from biz.account.models import UserProxy, Notification
from biz.workflow.serializers import WorkflowSerializer, BasicFlowInstanceSerializer
from cloud.instance_task import instance_create_task
from biz.instance.settings import INSTANCE_STATE_WAITING, INSTANCE_STATE_REJECTED


@require_GET
def instance_create_flow(request):

    instance_type = ContentType.objects.get(app_label="instance", model="instance")

    workflow = Workflow.objects.get(content_type=instance_type)

    return Response(WorkflowSerializer(workflow).data)


@require_POST
def update_instance_create_flow(request):

    workflow_id = request.data['workflow_id']
    step_ids = request.data.getlist('step_ids[]')
    step_names = request.data.getlist('step_names[]')
    step_auditors = request.data.getlist('step_auditors[]')

    workflow = Workflow.objects.get(pk=workflow_id)
    original_steps, new_steps = workflow.steps.all(), []
    step_orders = range(len(step_ids))

    last_step = None
    for index in step_orders:

        pk, name, auditor_id = step_ids[index], step_names[index], step_auditors[index]

        if pk:
            step = Step.objects.get(pk=pk)
        else:
            step = Step()
            step.workflow = workflow

        step.name = name
        step.order = index
        step.auditor = UserProxy.normal_users.get(pk=auditor_id)
        step.save()

        if last_step:
            last_step.next = step
            last_step.save()

        last_step = step

        new_steps.append(step)

    for step in original_steps:

        if step not in new_steps:
            step.delete()

    workflow = Workflow.objects.get(pk=workflow_id)

    return Response({"success": True,
                     "msg": _('Instance create flow is saved.'),
                     "data": WorkflowSerializer(workflow).data})


@require_GET
def flow_instances(request):

    role = request.query_params['role']

    if role == 'owner':
        instances = FlowInstance.objects.filter(owner=request.user)
    else:
        instances = FlowInstance.objects.filter(current_step__auditor=request.user,
                                                is_complete=False)

    serializer = BasicFlowInstanceSerializer(instances.order_by('-create_date'), many=True)
    return Response(serializer.data)


@require_POST
def approve(request):

    pk = request.data['id']
    instance = FlowInstance.objects.get(pk=pk)
    current_step = instance.current_step

    if current_step.next is None:
        instance.is_complete = True
    else:
        instance.current_step = current_step.next

    instance.save()

    if instance.is_complete:
        content_object = instance.content_object

        instance_create_task.delay(instance.content_object,
                                   password=instance.extra_data)

        content_object.status = INSTANCE_STATE_WAITING
        content_object.save()

        content = title = _('Your application for instance "%(instance_name)s" is approved! ') \
            % {'instance_name': content_object.name}
        Notification.info(instance.owner, title, content)
    return Response({"success": True,
                     "msg": _('This process is transfer to next phrase successfully!')})


@require_POST
def reject(request):

    pk, reason = request.data['id'], request.data['reason']

    instance = FlowInstance.objects.get(pk=pk)
    instance.reject_reason = reason
    instance.is_complete = True
    instance.save()

    instance.content_object.status = INSTANCE_STATE_REJECTED
    instance.content_object.save()

    content = title = _('Your application for instance "%(instance_name)s" is rejected! ') \
        % {'instance_name': instance.content_object.name}
    Notification.error(instance.owner, title, content)
    return Response({"success": True,
                     "msg": _('Application is rejected.')})


@require_GET
def workflow_status(request):
    num = FlowInstance.objects.filter(current_step__auditor=request.user,
                                      is_complete=False).count()
    return Response({'num': num})
