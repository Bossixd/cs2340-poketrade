from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile, ProfileCards
from pokemon.models import Card


class Trade(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    )

    # Trade participants
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_trades')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_trades')

    # Trade status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Currency offers
    sender_currency_offer = models.PositiveIntegerField(default=0)
    receiver_currency_offer = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Trade #{self.id}: {self.sender.user.username} -> {self.receiver.user.username} ({self.status})"

    def accept_trade(self):
        """Process the trade when accepted"""
        if self.status != 'pending':
            return False

        # Transfer currency
        if self.sender_currency_offer > 0:
            if self.sender.currency < self.sender_currency_offer:
                return False
            self.sender.currency -= self.sender_currency_offer
            self.receiver.currency += self.sender_currency_offer

        if self.receiver_currency_offer > 0:
            if self.receiver.currency < self.receiver_currency_offer:
                return False
            self.receiver.currency -= self.receiver_currency_offer
            self.sender.currency += self.receiver_currency_offer

        # Save profiles
        self.sender.save()
        self.receiver.save()

        # Transfer cards
        for trade_card in self.tradecards_set.filter(offered_by=self.sender):
            # Move the card from sender to receiver
            profile_card = ProfileCards.objects.get(profile=self.sender, cards=trade_card.card)
            profile_card.profile = self.receiver
            profile_card.save()

        for trade_card in self.tradecards_set.filter(offered_by=self.receiver):
            # Move the card from receiver to sender
            profile_card = ProfileCards.objects.get(profile=self.receiver, cards=trade_card.card)
            profile_card.profile = self.sender
            profile_card.save()

        # Update trade status
        self.status = 'accepted'
        self.save()
        return True

    def reject_trade(self):
        """Reject the trade"""
        if self.status != 'pending':
            return False

        self.status = 'rejected'
        self.save()
        return True

    def cancel_trade(self):
        """Cancel the trade (only sender can cancel)"""
        if self.status != 'pending':
            return False

        self.status = 'canceled'
        self.save()
        return True


class TradeCards(models.Model):
    """Cards offered in a trade"""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    offered_by = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.offered_by.user.username}'s {self.card.pokemon_info.name} in Trade #{self.trade.id}"