from django.contrib import admin
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response

from accounts.services.authentication_facade import AuthenticationFacade

from .models import User


def approve_user(modeladmin, request, queryset):
    auth_facade = AuthenticationFacade()

    result = []
    for user in queryset:
        approval_result = auth_facade.approve_user(user.id)
        result.append(f"User {user.user_name} approval result: {approval_result}")

    # Returning results in an admin message
    modeladmin.message_user(request, "\n".join(result))


approve_user.short_description = "Approve selected users"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "user_name",
        "is_approved",
        "is_active",
        "date_joined",
    ]
    actions = [approve_user]
