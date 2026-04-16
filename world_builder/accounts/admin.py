from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.forms import UserRegisterForm, UserUpdateForm
from accounts.models import User, Profile


# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ['avatar', 'first_name', 'last_name', 'date_of_birth', 'location', 'gender', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    model = User
    add_form = UserRegisterForm
    form = UserUpdateForm

    ordering = ['email']
    list_display = ['username', 'email', 'is_staff', 'is_active']

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['owner', 'first_name', 'last_name']
    search_fields = ['owner__username', 'first_name', 'last_name']
