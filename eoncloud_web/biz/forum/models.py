from django.db import models
from django.utils.translation import ugettext_lazy as _


class Forum(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(_('title'), null=False, blank=False, max_length=50)
    content = models.CharField(_('content'), null=False, blank=False, max_length=500)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    status = models.BooleanField(_("Close Status"), default=False)

    class Meta:
        db_table = "forum"


class ForumReply(models.Model):
    id = models.AutoField(primary_key=True)
    forum = models.ForeignKey('Forum')
    reply_content = models.CharField(_('content'), null=False, blank=False, max_length=500)
    user = models.ForeignKey('auth.User')
    user_data_center = models.ForeignKey('idc.UserDataCenter')
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "forum_reply"