from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import Profile, ProfileCards
from pokemon.models import Card
from .models import Trade, TradeCards


# Remove the problematic import
# from .forms import TradeForm

@login_required(login_url='auths:login')
def trade_list(request):
    """View all trades for the current user"""
    profile = Profile.objects.get(user=request.user)

    # Get all trades involving the current user
    sent_trades = Trade.objects.filter(sender=profile).order_by('-created_at')
    received_trades = Trade.objects.filter(receiver=profile).order_by('-created_at')

    pending_trades = Trade.objects.filter(
        Q(sender=profile) | Q(receiver=profile),
        status='pending'
    ).order_by('-created_at')

    completed_trades = Trade.objects.filter(
        Q(sender=profile) | Q(receiver=profile),
        status__in=['accepted', 'rejected', 'canceled']
    ).order_by('-created_at')

    context = {
        'profile': profile,
        'sent_trades': sent_trades,
        'received_trades': received_trades,
        'pending_trades': pending_trades,
        'completed_trades': completed_trades,
    }

    return render(request, 'trade/trade_list.html', context)


@login_required(login_url='auths:login')
def new_trade(request):
    """Create a new trade offer"""
    current_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # Get receiver username and validate
        receiver_username = request.POST.get('receiver_username')
        try:
            receiver_user = User.objects.get(username=receiver_username)
            receiver_profile = Profile.objects.get(user=receiver_user)

            # Can't trade with yourself
            if receiver_user == request.user:
                messages.error(request, "You cannot trade with yourself!")
                return redirect('trade:new_trade')

            # Can't trade with banned users
            if current_profile.is_banned or receiver_profile.is_banned:
                messages.error(request, "Cannot create trade - banned account involved.")
                return redirect('trade:trade_list')

        except (User.DoesNotExist, Profile.DoesNotExist):
            messages.error(request, f"User '{receiver_username}' does not exist!")
            return redirect('trade:new_trade')

        # Get currency offers
        try:
            sender_currency = int(request.POST.get('sender_currency', 0))
            receiver_currency = int(request.POST.get('receiver_currency', 0))

            # Validate currency amounts
            if sender_currency < 0 or receiver_currency < 0:
                messages.error(request, "Currency amounts cannot be negative!")
                return redirect('trade:new_trade')

            if sender_currency > current_profile.currency:
                messages.error(request, "You don't have enough coins for this trade!")
                return redirect('trade:new_trade')

        except ValueError:
            messages.error(request, "Invalid currency amount!")
            return redirect('trade:new_trade')

        # Create the trade
        trade = Trade.objects.create(
            sender=current_profile,
            receiver=receiver_profile,
            sender_currency_offer=sender_currency,
            receiver_currency_offer=receiver_currency
        )

        # Process selected cards from sender
        sender_cards = request.POST.getlist('sender_cards')
        for card_id in sender_cards:
            try:
                card = Card.objects.get(id=card_id)
                # Verify ownership
                if ProfileCards.objects.filter(profile=current_profile, cards=card).exists():
                    TradeCards.objects.create(
                        trade=trade,
                        card=card,
                        offered_by=current_profile
                    )
            except Card.DoesNotExist:
                pass

        # Process selected cards requested from receiver
        receiver_cards = request.POST.getlist('receiver_cards')
        for card_id in receiver_cards:
            try:
                card = Card.objects.get(id=card_id)
                # Verify ownership
                if ProfileCards.objects.filter(profile=receiver_profile, cards=card).exists():
                    TradeCards.objects.create(
                        trade=trade,
                        card=card,
                        offered_by=receiver_profile
                    )
            except Card.DoesNotExist:
                pass

        messages.success(request, f"Trade offer sent to {receiver_username}!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # GET request - show form
    # Get current user's cards and profile info
    user_cards = ProfileCards.objects.filter(profile=current_profile)

    context = {
        'profile': current_profile,
        'user_cards': user_cards,
    }

    return render(request, 'trade/new_trade.html', context)


@login_required(login_url='auths:login')
def trade_detail(request, trade_id):
    """View details of a specific trade"""
    trade = get_object_or_404(Trade, id=trade_id)
    current_profile = Profile.objects.get(user=request.user)

    # Only participants can view the trade
    if trade.sender != current_profile and trade.receiver != current_profile:
        messages.error(request, "You do not have permission to view this trade!")
        return redirect('trade:trade_list')

    # Get cards involved in this trade
    sender_cards = TradeCards.objects.filter(trade=trade, offered_by=trade.sender)
    receiver_cards = TradeCards.objects.filter(trade=trade, offered_by=trade.receiver)

    context = {
        'trade': trade,
        'sender_cards': sender_cards,
        'receiver_cards': receiver_cards,
        'current_profile': current_profile,
    }

    return render(request, 'trade/trade_detail.html', context)


@login_required(login_url='auths:login')
def search_user_cards(request):
    """AJAX endpoint to search for another user's cards"""
    username = request.GET.get('username', '')
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)

        # Get user's cards
        user_cards = ProfileCards.objects.filter(profile=profile)

        context = {
            'target_profile': profile,
            'user_cards': user_cards,
        }

        return render(request, 'trade/partials/user_cards.html', context)
    except (User.DoesNotExist, Profile.DoesNotExist):
        context = {'error': f"User '{username}' not found!"}
        return render(request, 'trade/partials/user_cards.html', context)


@login_required(login_url='auths:login')
def accept_trade(request, trade_id):
    """Accept a trade offer"""
    trade = get_object_or_404(Trade, id=trade_id)
    current_profile = Profile.objects.get(user=request.user)

    # Verify it's the receiver and trade is pending
    if trade.receiver != current_profile:
        messages.error(request, "Only the trade recipient can accept this trade!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    if trade.status != 'pending':
        messages.error(request, f"This trade is already {trade.status}!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # Check if receiver has enough currency
    if current_profile.currency < trade.receiver_currency_offer:
        messages.error(request, "You don't have enough coins to accept this trade!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # Check if sender still has enough currency
    if trade.sender.currency < trade.sender_currency_offer:
        messages.error(request, "The sender no longer has enough coins for this trade!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # Verify both users still own all offered cards
    sender_cards = TradeCards.objects.filter(trade=trade, offered_by=trade.sender)
    for trade_card in sender_cards:
        if not ProfileCards.objects.filter(profile=trade.sender, cards=trade_card.card).exists():
            messages.error(request, "The sender no longer owns all offered cards!")
            return redirect('trade:trade_detail', trade_id=trade.id)

    receiver_cards = TradeCards.objects.filter(trade=trade, offered_by=trade.receiver)
    for trade_card in receiver_cards:
        if not ProfileCards.objects.filter(profile=trade.receiver, cards=trade_card.card).exists():
            messages.error(request, "You no longer own all requested cards!")
            return redirect('trade:trade_detail', trade_id=trade.id)

    # Process the trade
    if trade.accept_trade():
        messages.success(request, "Trade accepted successfully!")
    else:
        messages.error(request, "There was an error processing the trade.")

    return redirect('trade:trade_detail', trade_id=trade.id)


@login_required(login_url='auths:login')
def reject_trade(request, trade_id):
    """Reject a trade offer"""
    trade = get_object_or_404(Trade, id=trade_id)
    current_profile = Profile.objects.get(user=request.user)

    # Verify it's the receiver and trade is pending
    if trade.receiver != current_profile:
        messages.error(request, "Only the trade recipient can reject this trade!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    if trade.status != 'pending':
        messages.error(request, f"This trade is already {trade.status}!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # Process the rejection
    if trade.reject_trade():
        messages.success(request, "Trade rejected.")
    else:
        messages.error(request, "There was an error rejecting the trade.")

    return redirect('trade:trade_detail', trade_id=trade.id)


@login_required(login_url='auths:login')
def cancel_trade(request, trade_id):
    """Cancel a trade offer (sender only)"""
    trade = get_object_or_404(Trade, id=trade_id)
    current_profile = Profile.objects.get(user=request.user)

    # Verify it's the sender and trade is pending
    if trade.sender != current_profile:
        messages.error(request, "Only the trade sender can cancel this trade!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    if trade.status != 'pending':
        messages.error(request, f"This trade is already {trade.status}!")
        return redirect('trade:trade_detail', trade_id=trade.id)

    # Process the cancellation
    if trade.cancel_trade():
        messages.success(request, "Trade canceled.")
    else:
        messages.error(request, "There was an error canceling the trade.")

    return redirect('trade:trade_detail', trade_id=trade.id)