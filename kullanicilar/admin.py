from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import YetkiliProfil, CalisanProfil

class YetkiliProfilInline(admin.StackedInline):
    model = YetkiliProfil
    can_delete = False
    verbose_name_plural = 'yetkili profil'


class CalisanProfilInline(admin.StackedInline):
    model = CalisanProfil
    can_delete= False
    verbose_name_plural='çalışan profil'

class UserAdmin(BaseUserAdmin):
    inlines =(YetkiliProfilInline, CalisanProfilInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

