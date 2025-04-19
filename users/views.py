from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .forms import RatingForm
from .models import Collection, Library, CD, Rating, FriendActivity, Profile
from django.contrib import messages
from django.db.models import Q


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
    return render(request, "users/profile.html")

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
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id)
        if not collection.is_public and collection.owner != request.user:
            return render(request, "users/collection_detail_limited.html", {
                "collection": collection
            })

    if request.user.profile.account_type == 'L':
        available_cds = CD.objects.exclude(id__in=collection.cds.values_list('id', flat=True))
    else:
        available_cds = CD.objects.filter(owner=request.user).exclude(id__in=collection.cds.values_list('id', flat=True))

    if request.method == "POST":
        # only add from library to collection
        cd_id = request.POST.get("cd_id")
        if cd_id:
            if request.user.profile.account_type == 'L':
                cd = get_object_or_404(CD, id=cd_id)
            else:
                cd = get_object_or_404(CD, id=cd_id, owner=request.user)
                
            collection.cds.add(cd)
            return redirect("collection_detail", collection_id=collection.id)
        
    return render(request, "users/collection_detail.html", {
        "collection": collection,
        "available_cds": available_cds,
        "is_librarian": request.user.profile.account_type == 'L',
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
    # allow librarians to edit any collection
    if request.user.profile.account_type == 'L':
        collection = get_object_or_404(Collection, id=collection_id)
    else:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            collection.name = name
            collection.save()
            return redirect("collection_detail", collection_id=collection.id)
    
    
    # if not POST or form invalid, redirect back to collection detail
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

@login_required
def public_item_view(request, cd_id):
    cd = get_object_or_404(CD, id=cd_id)
    user_rating = None

    # calc average rating
    ratings = cd.ratings.all()
    avg_rating = 0
    if ratings.exists():
        total = sum(r.rating_value for r in ratings)
        avg_rating = round(total / ratings.count(), 1)

    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, cd=cd)
        except Rating.DoesNotExist:
            pass
    
    user_collections = Collection.objects.filter(owner=request.user)
    
    is_owner = (cd.owner == request.user)
    is_librarian = (request.user.profile.account_type == 'L')
    can_add_to_collection = is_librarian or is_owner
    
    return render(request, "users/public_item.html", {
        "cd": cd,
        "user_rating": user_rating,
        "user_collections": user_collections,
        "is_owner": is_owner,
        "is_librarian": is_librarian,
        "can_add_to_collection": can_add_to_collection,
        "avg_rating": avg_rating,
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
