#coding=utf-8

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save


from biz.account.settings import USER_TYPE_CHOICES, QUOTA_ITEM, \
            RESOURCE_CHOICES, RESOURCE_ACTION_CHOICES


class UserProfile(models.Model): 
    user = models.ForeignKey(User, unique=True)
    mobile = models.CharField(_("Mobile"), max_length=26, null=True) 
    user_type = models.IntegerField(_("User Type"), null=True, default=1,\
                        choices=USER_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    class Meta:
        db_table = "auth_user_profile"
        verbose_name = _("UserProfile")
        verbose_name_plural = _("UserProfile")


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    udc = models.ForeignKey('idc.UserDataCenter')
    name = models.CharField(_("Contract name"), max_length=128, null=False)
    customer = models.CharField(_("Customer name"), max_length=128, null=False)
    start_date = models.DateTimeField(_("Start Date"), null=False)
    end_date = models.DateTimeField(_("End Date"), null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)

    def __unicode__(self):
        return self.name

    def get_quotas(self):
        d = settings.QUOTA_ITEMS.copy()
        for quota in self.quotas.all():
            d[quota.resource] = quota.limit
        return d
   
    class Meta:
        db_table = "user_contract"
        verbose_name = _("Contract")
        verbose_name_plural = _("Contract")


class Quota(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contract, related_name="quotas")
    resource = models.CharField(_("Resouce"), max_length=128, choices=QUOTA_ITEM, null=False)
    limit = models.IntegerField(_("Limit"), default=0)
    create_date = models.DateTimeField(_("Create Date"), default=timezone.now())
    deleted = models.BooleanField(_("Deleted"), default=False)

    class Meta:
        db_table = "user_quota"
        verbose_name = _("Quota")
        verbose_name_plural = _("Quota")


class Operation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    udc = models.ForeignKey('idc.UserDataCenter')

    resource = models.CharField(_("Resource"), max_length=128, null=False,
                choices=RESOURCE_CHOICES)
    resource_id = models.IntegerField(_("Resource ID"), null=False)
    resource_name = models.CharField(_("Resource Name"), max_length=128)
    action = models.CharField(_("Action"), max_length=128, null=False)
    result = models.IntegerField(_("Result"), default=0)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    @classmethod
    def log(cls, obj, obj_name, action, result):
        try:
            Operation.objects.create(
                user = obj.user,
                udc = obj.user_data_center,
                resource = obj.__class__.__name__,
                resource_id = obj.id,
                resource_name = obj_name,
                action = action,
                result = result
            )
        except Exception as e:
            pass

    def get_resource(self):
        return _(self.resource)

    def get_desc(self):  
        desc_format = _("%(resource)s:%(resource_name)s execute %(action)s operation")
        desc = desc_format % {
                "resource": _(self.resource),
                "resource_name": self.resource_name,
                "action": _(self.action),
               } 
        return desc

    class Meta:
        db_table = "user_operation"
        ordering = ['-create_date']
        verbose_name = _("Operation")
        verbose_name_plural = _("Operation")
