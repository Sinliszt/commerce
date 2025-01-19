from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits = 10, decimal_places = 2)
    image = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default = True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    winnger = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank = True, related_name="won_auctions")

    def current_bid(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.amount if highest_bid else self.starting_bid

    def highest_bidder(self):
        highest_bid = self.bids.order_by('-amount').first()
        return highest_bid.bidder if highest_bid else None
    
    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.listing.title}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete = models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.commenter.username} commented on {self.listing.title}"