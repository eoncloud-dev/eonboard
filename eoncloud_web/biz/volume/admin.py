from django.contrib import admin
from biz.volume.models import Volume


class VolumeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "size", "status")


admin.site.register(Volume, VolumeAdmin)


