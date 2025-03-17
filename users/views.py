from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from recordstar.models import CD

def index_view(request):
    return render(request, "users/index.html")

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
    # Ensure the current user is a librarian.
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("Only librarians can upgrade user accounts.")
    
    # Retrieve the target user.
    target_user = get_object_or_404(User, id=user_id)
    
    # Check that the target user's profile is set as patron ('P').
    if target_user.profile.account_type != 'P':
        return HttpResponse("Target user is either already a librarian or not eligible for upgrade.", status=400)
    
    if request.method == 'POST':
        # Perform the upgrade.
        target_user.profile.account_type = 'L'
        target_user.profile.save()
        return HttpResponse("User successfully upgraded to librarian.")
    else:
        # Render a confirmation page before proceeding.
        return render(request, 'users/confirm_upgrade.html', {'target_user': target_user})
