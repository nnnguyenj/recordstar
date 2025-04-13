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
def playlists_view(request):
    return render(request, "users/playlists.html")

@login_required
def recent_activity_view(request):
    from .models import Record, FriendActivity
    
    recent_friends = FriendActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]
    recent_records = Record.objects.filter(user=request.user).order_by('-created_at')[:5]
    #later: recent_ratings = Rating.objects.filter(user=request.user).order_by('-timestamp')[:5]
    return render(request, "users/recent_activity.html", {
        "recent_friends": recent_friends,
        "recent_records": recent_records,
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
def toggle_collection_privacy(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    collection.is_public = not collection.is_public
    collection.save()
    return redirect("collection")

@login_required
def add_collection_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            collection = Collection.objects.create(owner=request.user, name=name)
            return redirect("collection_detail", collection_id=collection.id)
    return render(request, "users/add_collection.html")

@login_required
def collection_detail_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    available_records = Record.objects.filter(user=request.user).exclude(id__in=collection.cds.values_list('id', flat=True))
    return render(request, "users/collection_detail.html", {
        "collection": collection,
        "available_records": available_records,
    })


@login_required
def add_record_to_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)

    if request.method == "POST":
        record_id = request.POST.get("record_id")
        if record_id:
            record = get_object_or_404(Record, id=record_id, user=request.user)
            collection.cds.add(record)
            return redirect("collection_detail", collection_id=collection.id)

    return redirect("collection_detail", collection_id=collection.id)

@login_required
def edit_collection_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            collection.name = name
            collection.save()
    return redirect("collection_detail", collection_id=collection.id)

@login_required
def delete_collection_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    if request.method == 'POST':
        collection.delete()
        return redirect("my_collections")
    return redirect("collection_detail", collection_id=collection.id)

@login_required
def remove_record_from_collection(request, collection_id, record_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    record = get_object_or_404(Record, id=record_id, user=request.user)
    collection.cds.remove(record)
    return redirect('collection_detail', collection_id=collection.id)
