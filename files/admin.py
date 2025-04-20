from django.contrib import admin

from .models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ["original_name", "user_user_name", "uploaded_at", "status"]
    search_fields = ["original_name", "user__user_name"]
    list_filter = ["status"]
    readonly_fields = ["guid", "uploaded_at"]
    date_hierarchy = "uploaded_at"
    fieldsets = [
        ("File Information", {"fields": ["original_name", "file", "user"]}),
        ("Status", {"fields": ["status", "error_message"]}),
        ("Metadata", {"fields": ["guid", "uploaded_at"], "classes": ["collapse"]}),
    ]

    def user_user_name(self, obj):
        return obj.user.user_name

    user_user_name.admin_order_field = "user__user_name"
    user_user_name.short_description = "User"


admin.site.register(File, FileAdmin)
