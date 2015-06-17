from django.contrib import admin


from biz.image.models import Image


class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "user")


admin.site.register(Image, ImageAdmin)
