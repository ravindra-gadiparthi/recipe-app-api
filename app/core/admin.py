from django.utils.translation import gettext as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tag, Ingredient


class CustomUserAdmin(UserAdmin):
    ordering = ['id']
    list_display = ['name', 'email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
