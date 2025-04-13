# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import DesiredCard, ElementType
from accounts.models import Profile, ProfileCards
from pokemon.models import Card
import random


def home(request):
    # Get all element types for the pack selection
    element_types = ['fire', 'water', 'grass', 'electric', 'psychic', 'fighting',
                     'dark', 'steel', 'fairy', 'dragon', 'colorless']

    # Get the user's desired card if authenticated
    desired_card = None
    profile = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            desired_card, created = DesiredCard.objects.get_or_create(profile=profile)
        except Profile.DoesNotExist:
            pass

    context = {
        'element_types': element_types,
        'desired_card': desired_card,
        'profile': profile
    }
    return render(request, 'marketplace/home.html', context)


@login_required
def set_desired(request):
    if request.method == "POST":
        card_id = request.POST.get("card_id")
        if card_id:
            profile = get_object_or_404(Profile, user=request.user)
            card = get_object_or_404(Card, id=card_id)

            # Get or create the desired card object
            desired_card, created = DesiredCard.objects.get_or_create(profile=profile)

            # Set the desired card and reset pity counter
            desired_card.card = card
            desired_card.reset_pity()

            messages.success(request, f"{card.pokemon_info.name} has been set as your desired card!")

    return redirect('marketplace:home')


@login_required
def roll(request):
    if request.method != "POST":
        return redirect('marketplace:home')

    element_type = request.POST.get("element_type")
    roll_type = request.POST.get("roll_type", "single")  # single or ten

    # Validate element type
    valid_types = ['fire', 'water', 'grass', 'electric', 'psychic', 'fighting',
                   'dark', 'steel', 'fairy', 'dragon', 'colorless']

    if element_type not in valid_types:
        messages.error(request, "Invalid element type selected.")
        return redirect('marketplace:home')

    # Get the user's profile
    profile = get_object_or_404(Profile, user=request.user)

    # Calculate cost
    cost = 1600 if roll_type == "ten" else 160

    # Check if user has enough currency
    if profile.currency < cost:
        messages.error(request, f"Not enough currency. You need {cost} currency to perform this roll.")
        return redirect('marketplace:home')

    # Deduct currency
    profile.currency -= cost
    profile.save()

    # Get or create desired card object
    desired_card, created = DesiredCard.objects.get_or_create(profile=profile)

    # Determine number of pulls
    num_pulls = 10 if roll_type == "ten" else 1

    # Perform the pulls
    pulled_cards = []

    for _ in range(num_pulls):
        # Each pull gives 5 cards
        pull_results = perform_pull(profile, element_type, desired_card)
        pulled_cards.extend(pull_results)

    context = {
        'pulled_cards': pulled_cards,
        'element_type': element_type,
        'profile': profile,
        'roll_type': roll_type
    }

    return render(request, 'marketplace/roll_results.html', context)


def perform_pull(profile, element_type, desired_card):
    # This function performs a single pull (5 cards)
    pulled_cards = []

    # Calculate the desired card chance:
    # Base chance is 1 in 1000 (0.1%), and every card pulled that is not desired adds 0.001% (1 in 100000).
    # After 450 cards (90 packs) have been pulled without the desired card, chance jumps to 6%.
    base_desired_chance = 0.1  # 0.1%
    if desired_card.pity_counter < 450:
        desired_chance = base_desired_chance + (desired_card.pity_counter * 0.001)
    else:
        desired_chance = 6.0

    # Set fixed rates for the other rarity buckets:
    high_hp_chance = 2.7  # High HP cards: HP > 130
    mid_hp_chance = 22.0  # Mid HP cards: HP 61-130
    low_hp_chance = 75.0  # Low HP cards: HP <= 60

    # Get cards of the selected element type
    element_cards = Card.objects.filter(type__icontains=element_type)
    low_hp_cards = element_cards.filter(hp__lte=60)
    mid_hp_cards = element_cards.filter(hp__gt=60, hp__lte=130)
    high_hp_cards = element_cards.filter(hp__gt=130)

    # Retrieve the desired card
    desired_card_obj = desired_card.card

    # For each of the 5 cards in a pull:
    for _ in range(5):
        roll = random.uniform(0, 100)
        candidate = None

        # Check for desired card chance first.
        if roll < desired_chance and desired_card_obj:
            candidate = desired_card_obj
            desired_card.reset_pity()  # Reset pity counter when desired card is obtained.
        elif roll < (desired_chance + high_hp_chance) and high_hp_cards.exists():
            candidate = random.choice(list(high_hp_cards))
            desired_card.increase_pity()
        elif roll < (desired_chance + high_hp_chance + mid_hp_chance) and mid_hp_cards.exists():
            candidate = random.choice(list(mid_hp_cards))
            desired_card.increase_pity()
        else:
            # Otherwise, award a low HP card.
            if low_hp_cards.exists():
                candidate = random.choice(list(low_hp_cards))
            else:
                candidate = random.choice(list(element_cards)) if element_cards.exists() else None
            desired_card.increase_pity()

        # NEW: For non-desired cards, there is a 50% chance to override with a card of a different element.
        if candidate and candidate != desired_card_obj:
            if random.random() < 0.5:
                # Define all valid element types.
                valid_types = ['fire', 'water', 'grass', 'electric', 'psychic', 'fighting',
                               'dark', 'steel', 'fairy', 'dragon', 'colorless']
                # Pick a random element type different than the current pack element.
                other_types = [t for t in valid_types if t != element_type]
                random_type = random.choice(other_types)

                # Determine the rarity bucket of the candidate by examining its HP.
                if candidate.hp <= 70:
                    alt_pool = Card.objects.filter(type__icontains=random_type, hp__lte=71)
                elif candidate.hp <= 140:
                    alt_pool = Card.objects.filter(type__icontains=random_type, hp__gt=79, hp__lte=140)
                else:
                    alt_pool = Card.objects.filter(type__icontains=random_type, hp__gt=140)

                if alt_pool.exists():
                    candidate = random.choice(list(alt_pool))

        if candidate:
            ProfileCards.objects.create(profile=profile, cards=candidate)
            pulled_cards.append(candidate)

    return pulled_cards