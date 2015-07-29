from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.
class Workflow(models.Model):
    name = models.CharField(_("Flow Name"), max_length=50)
    content_type = models.ForeignKey(ContentType, verbose_name=_("Content Type"), related_name="+")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "workflow"
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflow")

    @classmethod
    def get_instance_create_flow(cls):

        instance_type = ContentType.objects.get(app_label="instance", model="instance")

        return cls.objects.get(content_type=instance_type)


class Step(models.Model):
    workflow = models.ForeignKey(Workflow,
                                 related_name="steps", related_query_name="step",
                                 verbose_name=_("Work Flow"))
    name = models.CharField(_("Step Name"), max_length=50)
    auditor = models.ForeignKey(User, verbose_name=_("Auditor"), related_name="+")
    order = models.PositiveSmallIntegerField(_("Step No."))
    next = models.OneToOneField('workflow.Step', null=True,
                                related_name="previous",
                                related_query_name="previous")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "workflow_step"
        verbose_name = _("Workflow Step")
        verbose_name_plural = _("Workflow Steps")
        ordering = ("order", )

    @property
    def auditor_name(self):
        return self.auditor.username


class FlowInstance(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User',
                              related_name="process_list",
                              related_query_name="process")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    workflow = models.ForeignKey(Workflow, verbose_name=_("Work Flow"))
    current_step = models.ForeignKey('StepInstance', verbose_name=_("Current Step"), null=True, related_name="+")
    reject_reason = models.CharField(_("Reject Reason"), max_length=256)
    is_complete = models.BooleanField(_("Completed"), default=False)
    extra_data = models.TextField(_("Extra Data"), null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "workflow_instance"
        verbose_name = _("Workflow Instance")
        verbose_name_plural = _("Workflow Instances")

    @property
    def resource_name(self):
        return _('Instance')

    @property
    def owner_name(self):
        return self.owner.username

    @property
    def resource_info(self):
        instance = self.content_object
        return {'name': instance.name, 'cpu': instance.cpu, 'memory': instance.memory, 'sys_disk': instance.sys_disk}

    @property
    def steps(self):
        return self.step_set.all()

    @classmethod
    def create_instance_flow(cls, instance, owner, extra_data):

        workflow = Workflow.get_instance_create_flow()

        flow_instance = FlowInstance()
        flow_instance.content_object = instance
        flow_instance.workflow = workflow
        flow_instance.owner = owner
        flow_instance.name = _("Apply Instance")
        flow_instance.extra_data = extra_data
        flow_instance.save()

        last_step_instance, step_instances = None, []

        for step in workflow.steps.all():

            current_step_instance = StepInstance.objects.create(
                name=step.name, order=step.order,
                auditor=step.auditor, workflow=flow_instance)

            if last_step_instance:
                last_step_instance.next = current_step_instance
                last_step_instance.save()
            else:
                # If last_step_instance is none, then current_step_instance is
                # the first step
                flow_instance.current_step = current_step_instance
                flow_instance.save()
                pass

            last_step_instance = current_step_instance

        return flow_instance


class StepInstance(models.Model):
    workflow = models.ForeignKey(FlowInstance,
                                 related_name="step_set", related_query_name="step",
                                 verbose_name=_("Work Flow"))
    name = models.CharField(_("Step Name"), max_length=50)
    auditor = models.ForeignKey(User, verbose_name=_("Auditor"), related_name="+")
    order = models.PositiveSmallIntegerField(_("Step No."))
    next = models.OneToOneField('workflow.StepInstance', null=True,
                                related_name="previous",
                                related_query_name="previous")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "workflow_step_instance"
        verbose_name = _("Workflow Step")
        verbose_name_plural = _("Workflow Steps")
        ordering = ("order", )

    @property
    def auditor_name(self):
        return self.auditor.username
