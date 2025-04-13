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
    """Main marketplace view showing active listings"""

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


@login_required(login_url='auths:login')
def roll(request):
    """Summon random cards via the gacha system"""
    if request.method == 'GET':
        try:
            profile = Profile.objects.get(user=request.user)
            context = {
                'profile': profile,
                'single_roll_cost': 100,
                'multi_roll_cost': 850,  # 15% discount for multi roll
            }
            return render(request, 'marketplace/roll.html', context)

        except Profile.DoesNotExist:
            return redirect('auths:login')

    # The actual roll functionality would go here
    return render(request, 'marketplace/roll.html')