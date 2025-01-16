from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import get_user_model

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import AuctionListing, Category, Bid, Comment
from .forms import AuctionListingForm, BidForm, CommentForm

def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            User = get_user_model()
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing=form.save(commit=False)
            listing.owner = request.user
            listing.currentbid = form.cleaned_data['startingbid']
            listing.save()
            messages.success(request, "Your listing has been created")
            return redirect(reverse("index"))
    else:
        form = AuctionListingForm()
    return render(request, "auctions/create.html", {
        "form": form
    })

def listing_page(request, listing_id):
    listing=get_object_or_404(AuctionListing, pk=listing_id)
    bid_form = BidForm()
    comment_form = CommentForm()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form
    })

@login_required
def watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user in listing.watchlist.all():
        listing.watchlist.remove(request.user)
        messages.info(request, "Removed from your watchlist")
    else:
        listing.watchlist.add(request.user)
        messages.success(request, "Added to your watchlist")
    return redirect(reverse("listing_page", args=[listing_id]))

@login_required
def place_bid (request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    form=BidForm(request.POST)
    if form.is_valid():
        bid = form.cleaned_data['amount']
        if bid > (listing.currentbid or listing.startingbid):
            listing.currentbid = bid
            listing.save()
            Bid.objects.create(amount=bid, bidder=request.user, listing=listing)
            messages.success(request, "Bid placed successfully")
        else:
            messages.error(request, "Bid must be more than the current bid")
        return redirect(reverse("listing_page", args=[listing_id]))

@login_required
def close_auction (request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.user == listing.owner:
        highest_bid = listing.bids.order_by('-amount').first()
        listing.is_active = False
        listing.save()
        messages.success(request, f"Auction closed. Winner: {
            highest_bid.user.username 
            if highest_bid 
            else 'No bids placed'
            }")
    return redirect(reverse("listing_page", args=[listing_id]))

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories": categories
    })

def category_listing(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    listings = AuctionListing.objects.filter(category=category, is_active = True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })
