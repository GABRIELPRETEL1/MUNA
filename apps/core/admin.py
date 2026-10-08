from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Branch

admin.site.register(Branch)
admin.site.register(User, UserAdmin)
