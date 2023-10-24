from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username','first_name', 'last_name', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job', 'phone')}),
    )


@admin.register(Post)
class Postadmin(admin.ModelAdmin):
    list_display = ['author', 'created']
    ordering = ['author', 'created']
    list_filter = ['author', 'created']
    search_fields = ['created']
    raw_id_fields = ['author']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'created']
    ordering = ['active', 'created']
    list_filter = ['name', 'created']
    search_fields = ['created']


