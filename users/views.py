from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from recordstar.models import CD
from .models import Record
from .models import Profile

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
    return render(request, "users/recent_activity.html")

@login_required
def collection_view(request):
    cds = CD.objects.filter(owner=request.user)
    return render(request, "users/collection.html", {"cds": cds})

@login_required
def ratings_view(request):
    return render(request, "users/ratings.html")

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
    if request.method == 'POST':
        title = request.POST.get('title')
        artist = request.POST.get('artist')
        genre = request.POST.get('genre')
        release_date = request.POST.get('release_date')
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        Record.objects.create(
            user=request.user,
            title=title,
            artist=artist,
            genre=genre,
            release_date=release_date,
            rating=rating,
            review=review,
        )
        return redirect('collection')

    return render(request, 'users/add_record.html')

@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(Record, id=record_id, user=request.user)
    if request.method == 'POST':
        record.delete()
        return redirect('collection')
    else:
        return redirect('collection') #Or you could render a confirmation page.
    
@login_required
def add_friend(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    request.user.profile.friends.add(target_user.profile)
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
