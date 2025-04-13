from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Remove this as we're using the CustomUserAdmin from accounts app
# admin.site.unregister(User)

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'is_staff')
#     search_fields = ('username', 'email')
#     list_filter = ('is_staff', 'is_superuser', 'is_active')