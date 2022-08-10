from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "password",
    )
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    empty_value_display = "-пусто-"


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "-пусто-"
