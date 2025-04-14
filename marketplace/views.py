# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import DesiredCard, ElementType
from accounts.models import Profile, ProfileCards
from pokemon.models import Card
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import CardListing
from accounts.models import Profile, ProfileCards
from pokemon.models import Card


@login_required(login_url='auths:login')
def home(request):
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

    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-listed_at')  # Default: newest first
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    page = request.GET.get('page', 1)

    # Start with all active listings
    listings = CardListing.objects.filter(is_active=True)

    # Apply filters
    if search_query:
        listings = listings.filter(
            Q(card__pokemon_info__name__icontains=search_query) |
            Q(card__type__icontains=search_query)
        )

    if min_price:
        try:
            listings = listings.filter(price__gte=int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=int(max_price))
        except ValueError:
            pass

    # Apply sorting
    valid_sort_fields = ['price', '-price', 'listed_at', '-listed_at']
    if sort_by in valid_sort_fields:
        listings = listings.order_by(sort_by)
    else:
        listings = listings.order_by('-listed_at')  # Default sort

    # Paginate results
    paginator = Paginator(listings, 12)  # Show 12 listings per page
    listings_page = paginator.get_page(page)

    # Get current user's profile for currency display
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    context = {
        'listings': listings_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'profile': profile,
    }


    # Get filter parameters from request
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-listed_at')  # Default: newest first
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    page = request.GET.get('page', 1)

    # Start with all active listings
    listings = CardListing.objects.filter(is_active=True)

    # Apply filters
    if search_query:
        listings = listings.filter(
            Q(card__pokemon_info__name__icontains=search_query) |
            Q(card__type__icontains=search_query)
        )

    if min_price:
        try:
            listings = listings.filter(price__gte=int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=int(max_price))
        except ValueError:
            pass

    # Apply sorting
    valid_sort_fields = ['price', '-price', 'listed_at', '-listed_at']
    if sort_by in valid_sort_fields:
        listings = listings.order_by(sort_by)
    else:
        listings = listings.order_by('-listed_at')  # Default sort

    # Paginate results
    paginator = Paginator(listings, 12)  # Show 12 listings per page
    listings_page = paginator.get_page(page)

    # Get current user's profile for currency display
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    context = {
        'listings': listings_page,
        'search_query': search_query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'profile': profile,
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

@login_required(login_url='auths:login')
def my_listings(request):
    """View for displaying a user's own listings"""

    try:
        profile = Profile.objects.get(user=request.user)
        listings = CardListing.objects.filter(seller=profile)

        # Get filter parameters
        show_active = request.GET.get('active', 'all')

        if show_active == 'yes':
            listings = listings.filter(is_active=True)
        elif show_active == 'no':
            listings = listings.filter(is_active=False)

        context = {
            'listings': listings,
            'profile': profile,
            'show_active': show_active,
        }

        return render(request, 'marketplace/my_listings.html', context)
    except Profile.DoesNotExist:
        return redirect('accounts:profile')


@login_required(login_url='auths:login')
def list_card(request):
    """View for creating a new card listing"""

    if request.method == 'GET':
        try:
            profile = Profile.objects.get(user=request.user)

            # Get cards owned by the user that aren't already listed
            profile_cards = ProfileCards.objects.filter(profile=profile)

            # Exclude cards that are already listed and active
            active_listing_cards = CardListing.objects.filter(
                seller=profile,
                is_active=True
            ).values_list('card_id', flat=True)

            available_profile_cards = profile_cards.exclude(
                cards_id__in=active_listing_cards
            )

            context = {
                'profile': profile,
                'profile_cards': available_profile_cards,
            }

            return render(request, 'marketplace/list_card.html', context)

        except Profile.DoesNotExist:
            return redirect('accounts:profile')

    elif request.method == 'POST':
        try:
            card_id = request.POST.get('card_id')
            price = request.POST.get('price')

            # Validate inputs
            if not card_id or not price:
                messages.error(request, 'Please select a card and enter a price')
                return redirect('marketplace:list_card')

            try:
                price = int(price)
                if price < 1 or price > 999999:
                    messages.error(request, 'Price must be between 1 and 999,999')
                    return redirect('marketplace:list_card')
            except ValueError:
                messages.error(request, 'Price must be a valid number')
                return redirect('marketplace:list_card')

            profile = Profile.objects.get(user=request.user)
            card = Card.objects.get(id=card_id)

            # Check if the user owns this card
            if not ProfileCards.objects.filter(profile=profile, cards=card).exists():
                messages.error(request, 'You do not own this card')
                return redirect('marketplace:list_card')

            # Check if there's already an active listing for this card
            if CardListing.objects.filter(seller=profile, card=card, is_active=True).exists():
                messages.error(request, 'This card is already listed for sale')
                return redirect('marketplace:list_card')

            # Create the new listing
            CardListing.objects.create(
                seller=profile,
                card=card,
                price=price
            )

            messages.success(request, f'Your {card.pokemon_info.name} card has been listed for {price} coins')
            return redirect('marketplace:my_listings')

        except (Profile.DoesNotExist, Card.DoesNotExist):
            messages.error(request, 'An error occurred while processing your request')
            return redirect('marketplace:list_card')


@login_required(login_url='auths:login')
def cancel_listing(request, listing_id):
    """Cancel a card listing"""

    if request.method == 'POST':
        listing = get_object_or_404(CardListing, id=listing_id)

        # Verify the user is the seller
        if listing.seller.user != request.user:
            messages.error(request, 'You can only cancel your own listings')
            return redirect('marketplace:my_listings')

        # Deactivate the listing
        listing.is_active = False
        listing.save()

        messages.success(request, f'Your listing for {listing.card.pokemon_info.name} has been cancelled')

    return redirect('marketplace:my_listings')


@login_required(login_url='auths:login')
def buy_card(request, listing_id):
    """Purchase a card from the marketplace"""

    if request.method == 'POST':
        listing = get_object_or_404(CardListing, id=listing_id, is_active=True)

        try:
            buyer_profile = Profile.objects.get(user=request.user)

            # Check if buyer has enough currency
            if buyer_profile.currency < listing.price:
                messages.error(request, 'You do not have enough coins to buy this card')
                return redirect('marketplace:home')

            # Prevent buying your own card
            if listing.seller == buyer_profile:
                messages.error(request, 'You cannot buy your own card')
                return redirect('marketplace:home')

            # Process the transaction
            buyer_profile.currency -= listing.price
            buyer_profile.save()

            listing.seller.currency += listing.price
            listing.seller.save()

            # Transfer the card (we need to get the actual ProfileCards record)
            profile_card = listing.profile_card
            if profile_card:
                # Change the profile reference on this card
                profile_card.profile = buyer_profile
                profile_card.save()
            else:
                # If for some reason we can't find the original ProfileCards entry, create a new one
                ProfileCards.objects.create(
                    profile=buyer_profile,
                    cards=listing.card
                )

            # Mark listing as inactive
            listing.is_active = False
            listing.save()

            messages.success(request,
                             f'You have successfully purchased {listing.card.pokemon_info.name} for {listing.price} coins')

        except Profile.DoesNotExist:
            messages.error(request, 'An error occurred while processing your purchase')

    return redirect('marketplace:home')


@login_required
def roll(request):
    # Validate element type
    valid_types = ['fire', 'water', 'grass', 'electric', 'psychic', 'fighting',
                   'dark', 'steel', 'fairy', 'dragon', 'colorless']
    
    desired_card = DesiredCard.objects.get(profile=Profile.objects.get(user=request.user))
    
    if request.method != "POST":
        return render(request, 'marketplace/roll.html', context={'element_types': valid_types, 'desired_card': desired_card})

    element_type = request.POST.get("element_type")
    roll_type = request.POST.get("roll_type", "single")  # single or ten

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

@login_required(login_url='auths:login')
def buy_card(request, listing_id):
    """Purchase a card from the marketplace"""

    if request.method == 'POST':
        listing = get_object_or_404(CardListing, id=listing_id, is_active=True)

        try:
            buyer_profile = Profile.objects.get(user=request.user)

            # Check if buyer has enough currency
            if buyer_profile.currency < listing.price:
                messages.error(request, 'You do not have enough coins to buy this card')
                return redirect('marketplace:home')

            # Prevent buying your own card
            if listing.seller == buyer_profile:
                messages.error(request, 'You cannot buy your own card')
                return redirect('marketplace:home')

            # Process the transaction
            buyer_profile.currency -= listing.price
            buyer_profile.save()

            listing.seller.currency += listing.price
            listing.seller.save()

            # Transfer the card (we need to get the actual ProfileCards record)
            profile_card = listing.profile_card
            if profile_card:
                # Change the profile reference on this card
                profile_card.profile = buyer_profile
                profile_card.save()
            else:
                # If for some reason we can't find the original ProfileCards entry, create a new one
                ProfileCards.objects.create(
                    profile=buyer_profile,
                    cards=listing.card
                )

            # Mark listing as inactive
            listing.is_active = False
            listing.save()

            messages.success(request,
                             f'You have successfully purchased {listing.card.pokemon_info.name} for {listing.price} coins')

        except Profile.DoesNotExist:
            messages.error(request, 'An error occurred while processing your purchase')

    return redirect('marketplace:home')

@login_required(login_url='auths:login')
def my_listings(request):
    """View for displaying a user's own listings"""

    try:
        profile = Profile.objects.get(user=request.user)
        listings = CardListing.objects.filter(seller=profile)

        # Get filter parameters
        show_active = request.GET.get('active', 'all')

        if show_active == 'yes':
            listings = listings.filter(is_active=True)
        elif show_active == 'no':
            listings = listings.filter(is_active=False)

        context = {
            'listings': listings,
            'profile': profile,
            'show_active': show_active,
        }

        return render(request, 'marketplace/my_listings.html', context)
    except Profile.DoesNotExist:
        return redirect('accounts:profile')


@login_required(login_url='auths:login')
def list_card(request):
    """View for creating a new card listing"""

    if request.method == 'GET':
        try:
            profile = Profile.objects.get(user=request.user)

            # Get cards owned by the user that aren't already listed
            profile_cards = ProfileCards.objects.filter(profile=profile)

            # Exclude cards that are already listed and active
            active_listing_cards = CardListing.objects.filter(
                seller=profile,
                is_active=True
            ).values_list('card_id', flat=True)

            available_profile_cards = profile_cards.exclude(
                cards_id__in=active_listing_cards
            )

            context = {
                'profile': profile,
                'profile_cards': available_profile_cards,
            }

            return render(request, 'marketplace/list_card.html', context)

        except Profile.DoesNotExist:
            return redirect('accounts:profile')

    elif request.method == 'POST':
        try:
            card_id = request.POST.get('card_id')
            price = request.POST.get('price')

            # Validate inputs
            if not card_id or not price:
                messages.error(request, 'Please select a card and enter a price')
                return redirect('marketplace:list_card')

            try:
                price = int(price)
                if price < 1 or price > 999999:
                    messages.error(request, 'Price must be between 1 and 999,999')
                    return redirect('marketplace:list_card')
            except ValueError:
                messages.error(request, 'Price must be a valid number')
                return redirect('marketplace:list_card')

            profile = Profile.objects.get(user=request.user)
            card = Card.objects.get(id=card_id)

            # Check if the user owns this card
            if not ProfileCards.objects.filter(profile=profile, cards=card).exists():
                messages.error(request, 'You do not own this card')
                return redirect('marketplace:list_card')

            # Check if there's already an active listing for this card
            if CardListing.objects.filter(seller=profile, card=card, is_active=True).exists():
                messages.error(request, 'This card is already listed for sale')
                return redirect('marketplace:list_card')

            # Create the new listing
            CardListing.objects.create(
                seller=profile,
                card=card,
                price=price
            )

            messages.success(request, f'Your {card.pokemon_info.name} card has been listed for {price} coins')
            return redirect('marketplace:my_listings')

        except (Profile.DoesNotExist, Card.DoesNotExist):
            messages.error(request, 'An error occurred while processing your request')
            return redirect('marketplace:list_card')

