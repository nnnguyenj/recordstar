from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .models import Record
from .models import Profile
from .models import FriendActivity
from .models import Rating
from .forms import RatingForm
from .models import Collection
from recordstar.models import CD


def index_view(request):
    return render(request, "users/dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("recordstar/")

def google_login(request):
    if request.method == 'POST':
        account_type = request.POST.get('account_type', 'P')
        request.session['account_type'] = account_type
    return oauth2_login(request)

@login_required
def dashboard_view(request):
    context = {"user": request.user}
    # If current user is a librarian, retrieve all patron users.
    if request.user.profile.account_type == 'L':
        patrons = User.objects.filter(profile__account_type='P')
        context["patrons"] = patrons
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
    records = Record.objects.filter(user=request.user)
    return render(request, "users/collection.html", {"records": records})


@login_required
def my_collections_view(request):
    collections = request.user.collections.all()
    return render(request, "users/collections.html", {"collections": collections})

@login_required
def ratings_view(request):
    ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.save()
            return redirect('ratings')
    else:
        form = RatingForm()
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
        return HttpResponse("User successfully upgraded to librarian.")
    else:
        return render(request, 'users/confirm_upgrade.html', {'target_user': target_user})

@login_required
def add_record(request):
    from recordstar.models import CD

    if request.method == 'POST':
        cd_id = request.POST.get('cd_id')
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        cd = get_object_or_404(CD, id=cd_id)

        Record.objects.create(
            user=request.user,
            cd=cd,
            rating=rating,
            review=review,
        )
        return redirect('collection')

    all_cds = CD.objects.all()
    return render(request, 'users/add_record.html', {"all_cds": all_cds})


@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(Record, id=record_id, user=request.user)
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
def my_collections_view(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, "users/collection.html", {"collections": collections})

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

    # Restrict patrons from viewing private collection contents they don’t own
    if not collection.is_public and collection.owner != request.user:
        if request.user.profile.account_type == 'P':
            return render(request, "users/collection_detail_limited.html", {
                "collection": collection
            })

    available_cds = CD.objects.filter(owner=request.user).exclude(id__in=collection.cds.values_list('id', flat=True))

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
            collection.cds.add(cd)
            return redirect("collection_detail", collection_id=collection.id)

    return render(request, "users/collection_detail.html", {
        "collection": collection,
        "available_cds": available_cds,
    })


@login_required
def remove_cd_from_collection(request, collection_id, cd_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    cd = get_object_or_404(CD, id=cd_id, owner=request.user)
    if request.method == "POST":
        collection.cds.remove(cd)
    return redirect("collection_detail", collection_id=collection.id)

@login_required
def delete_collection_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        collection.delete()
        return redirect("collection")

    return render(request, "users/confirm_delete.html", {"collection": collection})

@login_required
def toggle_collection_privacy(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        collection.is_public = not collection.is_public
        collection.save()
    return redirect("collection_detail", collection_id=collection.id)

@login_required
def browse_collections(request):
    if request.user.profile.account_type == 'P':
        collections = Collection.objects.filter(is_public=True) | Collection.objects.filter(owner=request.user)
    else:
        collections = Collection.objects.all()

    return render(request, "users/browse_collections.html", {
        "collections": collections.distinct(),
    })


