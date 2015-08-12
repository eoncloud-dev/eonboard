#coding=utf-8

import logging
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from biz.account.settings import USER_TYPE_CHOICES, QUOTA_ITEM, NotificationLevel, TimeUnit

from biz.account.mixins import LivingDeadModel
from biz.idc.models import UserDataCenter

LOG = logging.getLogger(__name__)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    mobile = models.CharField(_("Mobile"), max_length=26, null=True)
    user_type = models.IntegerField(_("User Type"), null=True, default=1, \
                                    choices=USER_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    class Meta:
        db_table = "auth_user_profile"
        verbose_name = _("UserProfile")
        verbose_name_plural = _("UserProfile")


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class NormalUserManager(models.Manager):
    def get_queryset(self):
        return super(NormalUserManager, self).get_queryset().filter(is_superuser=False)


class SuperUserManager(models.Manager):
    def get_queryset(self):
        return super(SuperUserManager, self).get_queryset().filter(is_superuser=True)


class UserProxy(User):
    class Meta:
        proxy = True

    normal_users = NormalUserManager()

    super_users = SuperUserManager()

    @property
    def user_data_centers(self):
        return self.userdatacenter_set.all()

    @property
    def has_udc(self):
        return UserDataCenter.objects.filter(user=self).exists()


class LivingManager(models.Manager):
    def get_queryset(self):
        return super(LivingManager, self).get_queryset().filter(deleted=False)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(deleted=True)


class Contract(LivingDeadModel):
    user = models.ForeignKey(User)
    udc = models.ForeignKey('idc.UserDataCenter')
    name = models.CharField(_("Contract name"), max_length=128, null=False)
    customer = models.CharField(_("Customer name"), max_length=128, null=False)
    start_date = models.DateTimeField(_("Start Date"), null=False)
    end_date = models.DateTimeField(_("End Date"), null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    update_date = models.DateTimeField(_("Update Date"), auto_now_add=True, auto_now=True)

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


class Quota(LivingDeadModel):
    contract = models.ForeignKey(Contract, related_name="quotas")
    resource = models.CharField(_("Resouce"), max_length=128, choices=QUOTA_ITEM, null=False)
    limit = models.IntegerField(_("Limit"), default=0)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    update_date = models.DateTimeField(_("Update Date"), auto_now_add=True, auto_now=True)

    class Meta:
        db_table = "user_quota"
        verbose_name = _("Quota")
        verbose_name_plural = _("Quota")


class Operation(models.Model):
    user = models.ForeignKey(User)
    udc = models.ForeignKey('idc.UserDataCenter')

    resource = models.CharField(_("Resource"), max_length=128, null=False)
    resource_id = models.IntegerField(_("Resource ID"), null=False)
    resource_name = models.CharField(_("Resource Name"), max_length=128)
    action = models.CharField(_("Action"), max_length=128, null=False)
    result = models.IntegerField(_("Result"), default=0)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    @classmethod
    def log(cls, obj, obj_name, action, result=1, udc=None, user=None):

        try:
            Operation.objects.create(
                user=user or obj.user,
                udc=udc or obj.user_data_center,
                resource=obj.__class__.__name__,
                resource_id=obj.id,
                resource_name=obj_name,
                action=action,
                result=result
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

    @property
    def operator(self):
        return self.user.username

    @property
    def data_center_name(self):
        return self.udc.data_center.name

    class Meta:
        db_table = "user_operation"
        verbose_name = _("Operation")
        verbose_name_plural = _("Operation")


class Notification(models.Model):
    level = models.IntegerField(choices=NotificationLevel.OPTIONS, default=NotificationLevel.INFO)
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    is_announcement = models.BooleanField(default=False)
    is_auto = models.BooleanField(default=False)

    @property
    def time_ago(self):
        time_delta = (timezone.now() - self.create_date).total_seconds() * TimeUnit.SECOND

        if time_delta < TimeUnit.MINUTE:
            return _("just now")
        elif time_delta < TimeUnit.HOUR:
            minutes = time_delta / TimeUnit.MINUTE
            return _("%(minutes)d minutes ago") % {'minutes': minutes}
        elif time_delta < TimeUnit.DAY:
            hours = time_delta / TimeUnit.HOUR
            return _("%(hours)d hours ago") % {'hours': hours}
        elif time_delta < TimeUnit.YEAR:
            days = time_delta / TimeUnit.DAY
            return _("%(days)d days ago") % {'days': days}
        else:
            years = time_delta / TimeUnit.YEAR
            return _("%(years)d years ago") % {'years': years}

    class Meta:
        db_table = "notification"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    @classmethod
    def broadcast(cls, receivers, title, content, level):

        notification = cls.objects.create(title=title, content=content, level=level)
        for receiver in receivers:
            Feed.objects.create(receiver=receiver, notification=notification)

    @classmethod
    def pull_announcements(cls, receiver):

        try:
            for notification in Notification.objects.filter(is_announcement=True).\
                    exclude(feed=Feed.objects.filter(receiver=receiver)):

                Feed.objects.create(notification=notification, receiver=receiver)
        except:
            LOG.exception("Failed to pull announcement for user: %s", receiver.username)


NOTIFICATION_KEY_METHODS = ((NotificationLevel.INFO, 'info'),
                            (NotificationLevel.SUCCESS, 'success'), (NotificationLevel.ERROR, 'error'),
                            (NotificationLevel.WARNING, 'warning'), (NotificationLevel.DANGER, 'danger'))

# This loop will create some is_xxx(eg, is_info, is_success..) property
for value, name in NOTIFICATION_KEY_METHODS:
    def bind(level):
        setattr(Notification, 'is_' + name, property(lambda self: self.level == level))

    bind(value)

# This loop will create some action method, user can create notification like this way:
# Notification.info(receiver, title, content)
for value, name in NOTIFICATION_KEY_METHODS:

    def bind(level):

        def action(cls, receiver, title, content, is_auto=False):
            notification = cls.objects.create(title=title, content=content, level=level, is_auto=is_auto)
            Feed.objects.create(receiver=receiver, notification=notification)

            return notification

        setattr(Notification, name, classmethod(action))

    bind(value)


class Feed(LivingDeadModel):

    is_read = models.BooleanField(default=False)
    receiver = models.ForeignKey(User, related_name="notifications",
                                 related_query_name='notification')

    create_date = models.DateTimeField(auto_now_add=True)
    read_date = models.DateTimeField(null=True)
    deleted = models.BooleanField(default=False)
    notification = models.ForeignKey(Notification, related_name="feeds", related_query_name="feed")

    class Meta:
        db_table = "user_feed"
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")

    def mark_read(self):
        self.is_read = True
        self.read_date = timezone.now()
        self.save()

    def fake_delete(self):
        self.deleted = True
        self.mark_read()
