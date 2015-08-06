
import logging

from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework import status

from eoncloud_web.decorators import require_GET, require_POST
from biz.workflow.models import Workflow, Step, FlowInstance
from biz.account.models import UserProxy
from biz.workflow.serializers import WorkflowSerializer, BasicFlowInstanceSerializer
from biz.workflow.settings import ResourceType

from eoncloud_web.shortcuts import retrieve_params, retrieve_list_params


@require_GET
def workflow_list(request):
    serializer = WorkflowSerializer(Workflow.objects.all(), many=True)
    return Response(serializer.data)


@require_POST
def define_workflow(request):

    workflow_id, name, resource_type = retrieve_params(
        request.data, 'id', 'name', 'resource_type')

    step_ids, step_names, step_approvers = retrieve_list_params(
        request.data, 'step_ids[]', 'step_names[]', 'step_approvers[]')

    if workflow_id:
        workflow = Workflow.objects.get(pk=workflow_id)
    else:
        workflow = Workflow(is_default=False)

    workflow.name = name
    workflow.resource_type = resource_type
    workflow.save()

    original_steps, new_steps = workflow.steps.all(), []
    step_orders = range(len(step_ids))

    last_step = None
    for index in step_orders:

        pk, name, approver_id = step_ids[index], step_names[index], step_approvers[index]

        if pk:
            step = Step.objects.get(pk=pk)
        else:
            step = Step()
            step.workflow = workflow

        step.name = name
        step.order = index
        step.approver = UserProxy.normal_users.get(pk=approver_id)
        step.save()

        if last_step:
            last_step.next = step
            last_step.save()

        last_step = step

        new_steps.append(step)

    for step in original_steps:

        if step not in new_steps:
            step.delete()

    workflow = Workflow.objects.get(pk=workflow.pk)

    return Response({"success": True,
                     "msg": _('Workflow is saved.'),
                     "data": WorkflowSerializer(workflow).data})


@require_POST
def set_default_workflow(request):

    workflow_id, resource_type = retrieve_params(request.data, 'id', 'resource_type')

    try:
        workflow = Workflow.objects.get(pk=workflow_id)
    except Workflow.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        Workflow.objects.filter(resource_type=resource_type).update(is_default=False)
        workflow.is_default = True
        workflow.save()

    msg = _("%(name)s is the default workflow for %(resource)s now.") \
        % {'name': workflow.name, 'resource': workflow.resource_name}

    return Response({"success": True, "msg": msg}, status=status.HTTP_200_OK)


@require_POST
def cancel_default_workflow(request):

    workflow_id = request.data['id']

    try:
        workflow = Workflow.objects.get(pk=workflow_id)
    except Workflow.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        workflow.is_default = False
        workflow.save()

    msg = _("%(name)s is not default workflow anymore.") \
        % {'name': workflow.name, 'resource': workflow.resource_name}

    return Response({"success": True, "msg": msg}, status=status.HTTP_200_OK)


@require_POST
def delete_workflow(request):

    workflow_id = request.data['id']

    workflow = Workflow.objects.get(pk=workflow_id)

    workflow.steps.all().delete()

    workflow.delete()

    msg = _("Workflow %(name)s is deleted.") % {'name': workflow.name}

    return Response({"success": True, "msg": msg}, status=status.HTTP_200_OK)


@require_GET
def flow_instances(request):

    role = request.query_params['role']

    if role == 'applier':
        instances = FlowInstance.objects.\
            filter(owner=request.user).order_by('-create_date')[0:20]
    else:
        instances = FlowInstance.objects. \
            filter(current_step__approver=request.user,
                   is_complete=False).order_by('-create_date')

    serializer = BasicFlowInstanceSerializer(instances, many=True)
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
        instance.execute_predefined_action()

    return Response({"success": True,
                     "msg": _('This process is transferred to next phrase successfully!')})


@require_POST
def reject(request):

    pk, reason = request.data['id'], request.data['reason']

    instance = FlowInstance.objects.get(pk=pk)

    instance.reject(reason)

    return Response({"success": True, "msg": _('Application is rejected.')})


@require_GET
def workflow_status(request):
    num = FlowInstance.objects.filter(current_step__approver=request.user,
                                      is_complete=False).count()
    return Response({'num': num})


@require_GET
def resource_types(request):
    return Response(ResourceType.NAME_MAP)
