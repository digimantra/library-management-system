from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile within User admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline."""
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'get_active_member'
    )
    list_filter = BaseUserAdmin.list_filter + ('profile__is_active_member',)
    
    def get_active_member(self, obj):
        return obj.profile.is_active_member if hasattr(obj, 'profile') else False
    get_active_member.short_description = 'Active Member'
    get_active_member.boolean = True

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register User with new admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
