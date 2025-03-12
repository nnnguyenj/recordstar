from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate, login

# SHERRIFF: very basic index page created
from users.models import Profile


class IndexView(generic.TemplateView):
    template_name = "recordstar/index.html"
# Create your views here.

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile = Profile.objects.get(user=request.user)
        profile.image = request.FILES['profile_picture']
        profile.save()

        # Re-authenticate the user
        user = authenticate(request, username=request.user.username)
        if user:
            login(request, user)

        return redirect("/recordstar/")

    return render(request, "recordstar/upload_picture.html")

@login_required
def add_item(request):
    # Only allow librarians to access this view.
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("You do not have permission to access this page.")
    return render(request, 'recordstar/add_item.html')