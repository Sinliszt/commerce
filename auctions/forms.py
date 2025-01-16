from django import forms
from .models import AuctionListing, Bid, Comment

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'startingbid', 'image_url', 'category']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

