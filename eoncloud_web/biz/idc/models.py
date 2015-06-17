# -*- encoding:utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


class DataCenter(models.Model):
    """
    A data center is a mapper to backend openstack cluster 
    the config of project/user/password is for cloud-web api
    to create project and user
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Name"), max_length=255)
    host = models.CharField(_(u"openstack host"), null=False, blank=False, max_length=255, unique=True, help_text=_(u"IP of Compute Center"))
    project = models.CharField(_(u"default project"), null=False, blank=False, max_length=255,
                               help_text=_(u"Project Name of Data Center,recommended: admin"))
    user = models.CharField(_(u"default project user"), null=False, blank=False, max_length=255,
                            help_text=_(u"User who can visit the project"))
    password = models.CharField(_(u"default user password"), null=False, blank=False, max_length=255)
    auth_url = models.CharField(_(u"usually http://host:5000/v2.0"), null=False, blank=False, max_length=255)
    ext_net = models.CharField(_(u"External Network Name"), null=False, blank=False, max_length=255, default="net04_ext")

    @classmethod
    def get_default(cls):
        try:
            return cls.objects.filter().order_by('id')[0]
        except:
            return None

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "data_center"


class UserDataCenter(models.Model):
    """
    An user data center just like the project in openstack,
    when user registed in cloud-web we'll automatic create a project 
    with name "project-%(user-id)s"
    """
    id = models.AutoField(primary_key=True)
    data_center = models.ForeignKey(DataCenter) 
    user = models.ForeignKey('auth.User')
    tenant_name = models.CharField(_("Tenant"), max_length=255)
    tenant_uuid = models.CharField(_("Tenant UUID"), max_length=64)
    keystone_user = models.CharField(_("User"), max_length=255)
    keystone_password = models.CharField(_("Password"), max_length=255)
    

    def __unicode__(self):
        return "%s-%s" % (self.data_center.name, self.user.username)

    class Meta:
        db_table = "user_data_center"
