from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment, Category



admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)

# Register your models here.
