from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job', 'phone')}),
    )


def make_activation(modeladmin, request, queryset):
    result = queryset.update(active=False)
    modeladmin.message_user(request, f'{result}post were rejected')


make_activation.short_description = 'reject'


@admin.register(Post)
class Postadmin(admin.ModelAdmin):
    list_display = ['author', 'created']
    ordering = ['author', 'created']
    list_filter = ['author', 'created']
    search_fields = ['created']
    raw_id_fields = ['author']
    actions = [make_activation]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'created']
    ordering = ['active', 'created']
    list_filter = ['name', 'created']
    search_fields = ['created']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user_from', 'user_to']
