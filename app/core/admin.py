from django.contrib import admin

from core.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "role", "updated_at")
    search_fields = ("email", "display_name")
    list_filter = ("role",)
    readonly_fields = ("id", "created_at", "updated_at", "last_login_at")

