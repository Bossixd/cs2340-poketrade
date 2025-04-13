from django.contrib import admin
from .models import CardListing
from .models import ElementType, DesiredCard

admin.site.register(ElementType)
admin.site.register(DesiredCard)

@admin.register(CardListing)
class CardListingAdmin(admin.ModelAdmin):
    list_display = ('card', 'seller', 'price', 'is_active', 'listed_at')
    list_filter = ('is_active',)
    search_fields = ('card__pokemon_info__name', 'seller__user__username')
    readonly_fields = ('listed_at',)
    list_editable = ('is_active', 'price')

    fieldsets = (
        (None, {
            'fields': ('seller', 'card', 'price')
        }),
        ('Status', {
            'fields': ('is_active', 'listed_at')
        }),
    )