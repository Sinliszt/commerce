from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import get_user_model

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import admin, messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm

def index(request):
    listings = Listing.objects.filter(is_active=True)
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
        form = ListingForm(request.POST)
        if form.is_valid():
            listing=form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, "Your listing has been created")
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
    return render(request, "auctions/create.html", {
        "form": form
    })

def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bis = listing.bids.all()
    comments = listing.comments.all()
    is_owner = request.user == listing.owner
    has_won = request.user == listing.winner if listing.winner else False
    on_watchlist = request.user.is_authenticated and listing in request.user.watchlist.all()

    if request.method == "POST":
        if "bid" in request.POST:
            bid_form = BidForm(request.POST)
            comment_form = CommentForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commet = False)
                bid.listing = listing
                bid.bidder = request.user
                if bid.amount > listing.starting_bid and (not bids or bid.amount > max(b.amount for b in bids)):
                    bid.save()
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "bids": bids,
                        "comments": comments,
                        "error": "Bid must be higher than current bid",
                        "bid_form": bid_form,
                        "comment_form": comment_form,
                        "is_owner": is_owner,
                        "has_won": has_won
                    })
            elif "close" in request.POST and is_owner:
                listing.is_active = False
                listing.winner = listing.highest_bidder()
                listing.save()
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "bid_form": BidForm(),
        "comment_form": comment_form,
        "is_owner": is_owner,
        "has_won": has_won,
        "on_watchlist": on_watchlist
    })

@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html" {
        "listings": listings
    })