from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, ProfileCards
from django.utils.html import format_html
from django.urls import reverse

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'is_banned', 'user_status')
    list_editable = ('currency', 'is_banned')
    list_filter = ('is_banned', 'user__is_staff')
    search_fields = ('user__username',)
    actions = ['add_currency', 'reset_currency']
    readonly_fields = ('get_cards',)
    
    fieldsets = (
        (None, {'fields': ('user', 'currency', 'get_cards')}),
        ('Moderation', {
            'fields': ('is_banned',),
            'classes': ('collapse',),
        }),
    )
    
    def get_cards(self, obj):
        # Get all ProfileCards for this profile
        profile_cards = ProfileCards.objects.filter(profile=obj)
        
        # Create HTML links for each Card
        links = []
        for pc in profile_cards:
            url = reverse('admin:pokemon_card_change', args=(pc.cards.id,))
            links.append(
                f'<a href="{url}">{pc.cards.pokemon_info.name}</a>'
            )
        
        return format_html('<br>'.join(links)) if links else "No cards"
    
    get_cards.short_description = 'Cards'
    
    def user_status(self, obj):
        if obj.user.is_superuser:
            return "Superuser"
        return "Staff" if obj.user.is_staff else "Regular"
    user_status.short_description = 'Status'

    @admin.action(description='Add 1000 currency to selected')
    def add_currency(self, request, queryset):
        for profile in queryset:
            profile.currency += 1000
            profile.save()

    @admin.action(description='Reset currency to 1000')
    def reset_currency(self, request, queryset):
        queryset.update(currency=1000)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Currency & Status'
    fields = ('currency', 'is_banned')
    extra = 0

    def has_add_permission(self, request, obj):
        return False

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_currency', 'is_staff')

    def get_currency(self, obj):
        try:
            profile = Profile.objects.get(user=obj)
            return profile.currency
        except Profile.DoesNotExist:
            return "N/A"

    get_currency.short_description = 'Currency'


# Unregister the default UserAdmin and register our custom version
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileCards)