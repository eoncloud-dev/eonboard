from django.contrib import admin


from biz.backup.models import Backup


class BackupAdmin(admin.ModelAdmin):
    list_display = ("name", "user")


admin.site.register(Backup, BackupAdmin)
