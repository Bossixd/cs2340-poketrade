from django import template
from marketplace.models import DesiredCard

register = template.Library()

@register.simple_tag
def is_desired_card(profile, card):
    """Check if a card is set as the user's desired card"""
    try:
        desired = DesiredCard.objects.get(profile=profile)
        return desired.card == card
    except DesiredCard.DoesNotExist:
        return False