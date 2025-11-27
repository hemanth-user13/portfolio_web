from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *

class UserDetailsAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'profile_image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at',)


admin.site.register(UserDetails, UserDetailsAdmin)
admin.site.register(Salutations)
admin.site.register(Titles)
admin.site.register(FakeProductsData)
admin.site.register(Products)
admin.site.register(Movies)


class PartnerAdminLayout(admin.ModelAdmin):
    list_display = ('name', 'address', 'zip_code', 'mobile_number')


admin.site.register(Partners, PartnerAdminLayout)