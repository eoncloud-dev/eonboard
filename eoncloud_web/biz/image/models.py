from django.db import models
from django.utils.translation import ugettext_lazy as _


IMAGE_OS_TYPE = (
    (1, _("Windows")),
    (2, _("Linux")),
)

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Image Name"), max_length=255)
    uuid = models.CharField(_("UUID"), max_length=255, help_text=_("Openstack Image UUID"))
    login_name = models.CharField(_("Login Name"), max_length=255)
    os_type = models.PositiveIntegerField(_("Image OS Type"), choices=IMAGE_OS_TYPE)

    data_center = models.ForeignKey('idc.DataCenter')
    user = models.ForeignKey('auth.User', null=True, blank=True, default=None)

    create_at = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
        db_table = "image"
