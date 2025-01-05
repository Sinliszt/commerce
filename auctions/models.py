from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class AuctionListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    startingbid = models.DecimalField(max_digits = 10, decimal_places = 2)
    currentbid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null= True, related_name="listings")
    createdat = models.DateTimeField(auto_now_add = True)
    is_active = models.BooleanField(default = True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return self.title

class Bid(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    createdat = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.bidder} bid {self.bid_amount} on {self.listing.title}"

class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete = models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete = models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.commenter} commented on {self.listing.title}"


