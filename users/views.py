from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import RatingForm
from .models import Collection, Library, CD, Rating, FriendActivity, Profile, CDRequest, CDRequestAccess
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone


def index_view(request):
    return render(request, "users/dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("account_login")

def google_login(request):
    if request.method == 'POST':
        account_type = request.POST.get('account_type', 'P')
        request.session['account_type'] = account_type
    return oauth2_login(request)

@login_required
def dashboard_view(request):
    context = {"user": request.user}
    
    # get CDs not in any collection or in public collections
    # distinct() removes duplicates
    public_cds = CD.objects.filter(
        Q(collections__isnull=True) | 
        Q(collections__is_public=True)
    ).distinct()

    context["public_cds"] = public_cds
    context["is_anon"] = request.user.is_anonymous

    return render(request, "users/dashboard.html", context)

@login_required
def recent_activity_view(request):
    recent_friends = FriendActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]
    recent_collections = Collection.objects.filter(owner=request.user).order_by('-created_at')[:5]
    recent_ratings = Rating.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, "users/recent_activity.html", {
        "recent_friends": recent_friends,
        "recent_collections": recent_collections,
        "recent_ratings": recent_ratings,
    })

@login_required
def collection_view(request):
    records = CD.objects.filter(user=request.user)
    return render(request, "users/collection.html", {"records": records})


@login_required
def my_collections_view(request):
    collections = request.user.collections.all()
    return render(request, "users/collection.html", {"collections": collections})

@login_required
def ratings_view(request):
    ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = RatingForm(request.POST, user=request.user)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.save()
            return redirect('ratings')
    else:
        form = RatingForm(user=request.user)

    context = {
        'ratings': ratings,
        'form': form,
    }
    return render(request, 'users/ratings.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile = request.user.profile
        profile.image = request.FILES['profile_picture']
        profile.save()
        messages.success(request, "Profile picture updated.")
        return redirect('profile')  # make sure this matches your URL name
    
    return render(request, "users/profile.html")

@login_required
def edit_profile_info(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if username and email:
            request.user.username = username
            request.user.email = email
            request.user.save()
            messages.success(request, "Profile updated successfully.")
        else:
            messages.error(request, "Username and email are required.")

    return redirect('profile')  # make sure 'profile' is a valid URL name

@login_required
def settings_view(request):
    return render(request, "users/settings.html")

@login_required
def upgrade_user_to_librarian(request, user_id):
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("Only librarians can upgrade user accounts.")
    
    target_user = get_object_or_404(User, id=user_id)
    
    if target_user.profile.account_type != 'P':
        return HttpResponse("Target user is either already a librarian or not eligible for upgrade.", status=400)
    
    if request.method == 'POST':
        target_user.profile.account_type = 'L'
        target_user.profile.save()
        # Add success message and redirect
        messages.success(request, f"Success! Upgraded {target_user.username} to a Librarian!")
        return redirect('librarians')
    else:
        return render(request, 'users/confirm_upgrade.html', {'target_user': target_user})


@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(CD, id=record_id, user=request.user)
    if request.method == 'POST':
        record.delete()
        return redirect("collection")
    else:
        return redirect("collection")
    
@login_required
def add_friend(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    request.user.profile.friends.add(target_user.profile)
    #log recent friend activity
    FriendActivity.objects.create(user=request.user, friend=target_user)
    return redirect('friends')

@login_required
def remove_friend(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    request.user.profile.friends.remove(target_user.profile)
    return redirect('friends')

@login_required
def friends_view(request):
    all_users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)
    friends = request.user.profile.friends.all()
    return render(request, "users/friends.html", {
        "friends": friends,
        "all_users": all_users,
    })

@login_required
def librarians_view(request):
    librarians = User.objects.filter(profile__account_type='L')
    context = {
        "librarians": librarians,
    }
    if request.user.profile.account_type == 'L':
        patrons = User.objects.filter(profile__account_type='P')
        context["patrons"] = patrons
    
    return render(request, "users/librarians_list.html", context)

@login_required
def my_collections_view(request):
    # Get the user's own collections
    own_collections = Collection.objects.filter(owner=request.user)
    
    # Initialize other_collections as None
    other_collections = None
    
    # If user is a librarian, get all other collections
    if request.user.profile.account_type == 'L':
        other_collections = Collection.objects.exclude(owner=request.user)
    
    return render(request, "users/collection.html", {
        "own_collections": own_collections,
        "other_collections": other_collections,
        "is_librarian": request.user.profile.account_type == 'L'
    })

@login_required
def add_collection_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            is_public = True if request.user.profile.account_type == 'P' else request.POST.get("is_public") == "on"
            Collection.objects.create(owner=request.user, name=name, is_public=is_public)
            return redirect("collection")
    return render(request, "users/add_collection.html")

@login_required
def collection_detail_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    has_access = (
            collection.is_public or
            request.user == collection.owner or
            request.user.profile.account_type == 'L' or
            CDRequestAccess.objects.filter(
                requester=request.user,
                collection=collection,
                approved=True
            ).exists()
    )

    if not has_access:
        has_requested = CDRequestAccess.objects.filter(requester=request.user, collection=collection).exists()
        return render(request, "users/collection_detail_limited.html", {
            "collection": collection,
            "has_requested": has_requested,
        })

    is_librarian = request.user.profile.account_type == 'L'
    if is_librarian:
        available_cds = CD.objects.exclude(id__in=collection.cds.values_list('id', flat=True))
    else:
        available_cds = CD.objects.filter(owner=request.user).exclude(id__in=collection.cds.values_list('id', flat=True))

    if request.method == "POST":
        cd_id = request.POST.get("cd_id")
        if cd_id:
            cd = get_object_or_404(CD, id=cd_id)
            collection.cds.add(cd)
            return redirect("collection_detail", collection_id=collection.id)

    query = request.GET.get("q", "").strip()
    cds = collection.cds.all()
    if query:
        cds = cds.filter(
            Q(title__icontains=query) |
            Q(artist__icontains=query) |
            Q(unique_code__icontains=query) |
            Q(genre__icontains=query) |
            Q(release_year__icontains=query)
        )

    return render(request, "users/collection_detail.html", {
        "collection": collection,
        "available_cds": available_cds,
        "is_librarian": is_librarian,
        "cds": cds,
        "query": query,
    })




@login_required
def remove_cd_from_collection(request, collection_id, cd_id):
    # allow librarians to remove CDs from any collection
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    
    cd = get_object_or_404(CD, id=cd_id)
    if request.method == "POST":
        collection.cds.remove(cd)
    return redirect("collection_detail", collection_id=collection.id)

@login_required
def delete_collection_view(request, collection_id):
    # allow librarians to delete any collection
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        collection.delete()
        return redirect("collection")

    return render(request, "users/confirm_delete.html", {"collection": collection})

@login_required
def edit_collection(request, collection_id):
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            collection.name = name

            # Only librarians can change is_public
            if request.user.profile.account_type == 'L':
                collection.is_public = request.POST.get("is_public") == "on"

            collection.save()
            return redirect("collection_detail", collection_id=collection.id)

    return redirect("collection_detail", collection_id=collection.id)


@login_required
def toggle_collection_privacy(request, collection_id):
    # allow librarians to toggle privacy for any collection
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        collection.is_public = not collection.is_public
        collection.save()
    return redirect("collection_detail", collection_id=collection.id)

# LIBRARY VIEWS

@login_required
def library_view(request):
    # librarians get all CDs, patrons only their own
    if request.user.profile.account_type == 'L':
        user_cds = CD.objects.all()
    else:
        user_cds = CD.objects.filter(owner=request.user)
    
    cd_info = []
    for cd in user_cds:
        if request.user.profile.account_type == 'L':
            collection = cd.collections.first()
            is_owned = cd.owner == request.user
        else:
            collection = cd.collections.filter(owner=request.user).first()
            is_owned = True  # always true for patrons (only shows their CDs)
        
        cd_info.append({
            'cd': cd,
            'collection': collection,
            'is_owned': is_owned
        })
    
    user_collections = Collection.objects.filter(owner=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        artist = request.POST.get("artist")
        genre = request.POST.get("genre")
        release_year = request.POST.get("release_year")
        description = request.POST.get("description")

        # cover image required
        if 'cover_image' not in request.FILES:
            return render(request, "users/library.html", {
                "cd_info": cd_info,
                "error": "Cover image is required",
                "is_librarian": request.user.profile.account_type == 'L',
                "form_data": {
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "release_year": release_year,
                    "description": description,
                }
            })
        
        if title and artist:
            cd = CD.objects.create(
                title=title,
                artist=artist,
                genre=genre,
                release_year=release_year or None,
                description=description or "",
                owner=request.user,
            )
            cd.cover_image = request.FILES['cover_image']
            cd.save()

            return redirect("library")
    
    return render(request, "users/library.html", {
        "cd_info": cd_info,
        "is_librarian": request.user.profile.account_type == 'L',
        "user_collections": user_collections,
    })

@login_required
def add_cd_to_library(request):
    if request.method == "POST":
        title = request.POST.get("title")
        artist = request.POST.get("artist")
        genre = request.POST.get("genre")
        release_year = request.POST.get("release_year")

        if title and artist:
            cd = CD.objects.create(
                title=title,
                artist=artist,
                genre=genre,
                release_year=release_year or None,
                owner=request.user,
            )
            return redirect("library")
    
    return render(request, "users/add_cd.html")

@login_required
def delete_cd(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id, owner=request.user)
    if request.method == "POST":
        cd.delete()
    return redirect("library")

@login_required
def edit_cd(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id, owner=request.user)
    
    if request.method == "POST":
        title = request.POST.get("title")
        artist = request.POST.get("artist")
        genre = request.POST.get("genre")
        release_year = request.POST.get("release_year")
        description = request.POST.get("description")
        
        if not cd.cover_image and 'cover_image' not in request.FILES:
            return render(request, "users/edit_cd.html", {
                "cd": cd,
                "error": "Cover image is required",
                "form_data": {
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "release_year": release_year,
                    "description": description,
                }
            })
        
        cd.title = title
        cd.artist = artist
        cd.genre = genre
        cd.release_year = release_year or None
        cd.description = description
        
        if 'cover_image' in request.FILES:
            cd.cover_image = request.FILES['cover_image']
        cd.save()
        return redirect("library")
    
    return render(request, "users/edit_cd.html", {"cd": cd})

# had to take out the login required so anon users can see it 
def public_item_view(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)
    user_rating = None
    user_collections = None
    is_owner = False
    is_librarian = False
    can_add_to_collection = False
    has_pending_request = False

    # Calculate average rating
    ratings = cd.ratings.all()
    avg_rating = round(sum(r.rating_value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

    # If user is logged in, fetch personalized data
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, cd=cd)
        except Rating.DoesNotExist:
            pass

        user_collections = Collection.objects.filter(owner=request.user)
        is_owner = cd.owner == request.user
        is_librarian = request.user.profile.account_type == 'L'
        can_add_to_collection = is_librarian or is_owner

        has_pending_request = CDRequest.objects.filter(
            cd=cd, 
            requester=request.user, 
            status='pending'
        ).exists()

    is_public = cd.is_public()

    return render(request, "users/public_item.html", {
        "cd": cd,
        "user_rating": user_rating,
        "user_collections": user_collections,
        "is_owner": is_owner,
        "is_librarian": is_librarian,
        "can_add_to_collection": can_add_to_collection,
        "avg_rating": avg_rating,
        "has_pending_request": has_pending_request,
        "is_public": is_public,
    })

@login_required
def add_to_collection(request, collection_id, cd_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    cd = get_object_or_404(CD, id=cd_id)
    
    if request.user.profile.account_type != 'L' and cd.owner != request.user:
        messages.error(request, "As a patron, you can only add your own CDs to collections.")
        return redirect('public_item', cd_id=cd_id)
    
    if request.method == "POST":
        collection.cds.add(cd)
        messages.success(request, f"Added '{cd.title}' to collection '{collection.name}'.")
    
    return redirect('public_item', cd_id=cd_id)

@login_required
def rate_cd_public(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)
    
    if request.method == 'POST':
        form_data = {
            'rating_value': request.POST.get('rating_value'),
            'review': request.POST.get('review')
        }
        
        # check for existing rating by this user
        try:
            rating = Rating.objects.get(user=request.user, cd=cd)
            rating.rating_value = form_data['rating_value']
            rating.review = form_data['review']
            rating.save()
            messages.success(request, 'Your rating has been updated.')
        except Rating.DoesNotExist:
            Rating.objects.create(
                user=request.user,
                cd=cd,
                rating_value=form_data['rating_value'],
                review=form_data['review']
            )
            messages.success(request, 'Your rating has been submitted.')
        
    return redirect('public_item', cd_id=cd.id)

@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    
    if request.method == 'POST' or request.method == 'GET':
        cd_id = rating.cd.id
        rating.delete()
        
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
            
        messages.success(request, 'Rating deleted successfully.')
        return redirect('ratings')
        
    return redirect('ratings')

@login_required
def add_cd_to_collection(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)
    collection_id = request.POST.get("collection_id")

    # patrons can only add their own CDs
    if request.user.profile.account_type != 'L' and cd.owner != request.user:
        return HttpResponseForbidden("Patrons can only add their own CDs to collections.")

    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        collection.cds.add(cd)
        messages.success(request, f"Added '{cd.title}' to '{collection.name}'.")
    
    return redirect("library")

@login_required
def create_collection_with_cd(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)

    # patrons can only add their own CDs
    if request.user.profile.account_type != 'L' and cd.owner != request.user:
        return HttpResponseForbidden("Patrons can only create collections with their own CDs.")

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            is_public = True if request.user.profile.account_type == 'P' else request.POST.get("is_public") == "on"
            collection = Collection.objects.create(owner=request.user, name=name, is_public=is_public)
            collection.cds.add(cd)
            messages.success(request, f"Created collection '{collection.name}' and added '{cd.title}'.")
    
    return redirect("library")

@login_required
def delete_profile_picture(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.image = 'profile_pics/default.jpg'
        profile.save()
        messages.success(request, "Profile picture reset to default.")
    return redirect('profile')  # or whatever your profile view name is


def search_results(request):
    query = request.GET.get('q', '').strip()
    user = request.user

    cd_results = []
    collection_results = []

    if query:
        cd_results = CD.objects.filter(
            Q(title__icontains=query) |
            Q(artist__icontains=query) |
            Q(unique_code__icontains=query) |
            Q(genre__icontains=query) |
            Q(release_year__icontains=query)
        ).distinct()

        cd_results = cd_results.filter(
            Q(collections__isnull=True) |
            Q(collections__is_public=True) |
            Q(owner=user)
        ).distinct()

        collection_results = Collection.objects.filter(
            Q(name__icontains=query),
            Q(is_public=True) | Q(owner=user)
        ).distinct()

    return render(request, 'users/search_results.html', {
        'query': query,
        'cd_results': cd_results,
        'collection_results': collection_results,
    })
# lending views

@login_required
def request_cd(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)
    
    # Check if CD is available and public
    if cd.status != 'available' or not cd.is_public():
        messages.error(request, "This CD is not available for borrowing.")
        return redirect('public_item', cd_id=cd.id)
    
    # Check if user already has a pending request for this CD
    if CDRequest.objects.filter(cd=cd, requester=request.user, status='pending').exists():
        messages.info(request, "You already have a pending request for this CD.")
        return redirect('public_item', cd_id=cd.id)
    
    if request.method == 'POST':
        requested_days = int(request.POST.get('requested_days', 7))
        
        # Create request
        cd_request = CDRequest.objects.create(
            cd=cd,
            requester=request.user,
            requested_days=requested_days
        )
        
        messages.success(request, f"Request sent to {cd.owner.username} for '{cd.title}'")
        return redirect('my_requests')
    
    return render(request, 'users/request_cd.html', {'cd': cd})

@login_required
def my_requests(request):
    # Get requests made by the user
    sent_requests = CDRequest.objects.filter(requester=request.user).order_by('-request_date')
    
    # Get requests for user's CDs
    received_requests = CDRequest.objects.filter(cd__owner=request.user).order_by('-request_date')
    
    return render(request, 'users/my_requests.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

@login_required
def respond_to_request(request, request_id):
    cd_request = get_object_or_404(CDRequest, id=request_id, cd__owner=request.user)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        
        if response == 'approve':
            cd_request.status = 'approved'
            cd_request.response_date = timezone.now()
            
            # Update CD status
            cd = cd_request.cd
            cd.status = 'checked_out'
            cd.checked_out_to = cd_request.requester
            
            # Calculate due date
            due_date = timezone.now().date() + timezone.timedelta(days=cd_request.requested_days)
            cd.due_date = due_date
            
            cd.save()
            cd_request.save()
            
            messages.success(request, f"You've approved the request. '{cd.title}' is now checked out to {cd_request.requester.username}.")
        
        elif response == 'reject':
            cd_request.status = 'rejected'
            cd_request.response_date = timezone.now()
            cd_request.save()
            messages.info(request, "Request rejected.")
        
        return redirect('my_requests')
    
    return render(request, 'users/respond_to_request.html', {'cd_request': cd_request})

@login_required
def return_cd(request, request_id):
    # Allow both the borrower and the owner to mark as returned
    cd_request = get_object_or_404(
        CDRequest, 
        Q(requester=request.user) | Q(cd__owner=request.user),
        id=request_id,
        status='approved'
    )
    
    if request.method == 'POST':
        cd_request.status = 'returned'
        cd_request.return_date = timezone.now()
        
        # Update CD status
        cd = cd_request.cd
        cd.status = 'available'
        cd.checked_out_to = None
        cd.due_date = None
        
        cd.save()
        cd_request.save()
        
        messages.success(request, f"'{cd.title}' has been marked as returned.")
        return redirect('my_requests')
    
    return render(request, 'users/return_cd.html', {'cd_request': cd_request})


def anon_user_view(request):
    # Pull CDs not in a collection or in public collections
    public_cds = CD.objects.filter(
        Q(collections__isnull=True) | Q(collections__is_public=True)
    ).distinct()

    context = {
        "public_cds": public_cds
    }

    return render(request, "recordstar/anon_user_welcome.html", context)

# views.py
@login_required
def request_access(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    # Disallow access requests for public collections or for owners
    if collection.is_public or collection.owner == request.user:
        return redirect('collection_detail', collection_id=collection.id)

    CDRequestAccess.objects.get_or_create(
        requester=request.user,
        collection=collection
    )

    return redirect('collection_detail', collection_id=collection.id)
