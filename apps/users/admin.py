from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'joined_date', 'register_provider')
    list_filter = ('is_staff', 'is_active', 'groups', 'register_provider')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': (
            'avatar', 'background_photo', 'social_links', 'amount_of_lookups', 'custom_prompt_price',
            'register_provider', 'sale_notification_emails',
        )}),
        ('Settings', {'fields': (
            'hide_categories', 'hide_tone_style', 'hide_fast_prompt', 'new_favorites_emails', 'new_followers_emails',
            'new_messages_emails', 'new_job_emails', 'new_review_emails', 'new_credits_emails', 'review_reminder_emails',
            'following_users_new_prompts',
        )}),
    )

admin.site.register(User, CustomUserAdmin)


@admin.register(Subscription)
@admin.register(Like)
class TwoUserActionsAdmin(admin.ModelAdmin):
    model = Like
    list_display = ('sender', 'receiver', 'created_date')
    search_fields = ('sender__username', 'receiver__username', 'sender__email', 'receiver__email')

admin.site.register(User, CustomUserAdmin)
