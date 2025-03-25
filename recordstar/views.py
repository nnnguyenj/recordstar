from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate, login
from .models import CD

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
def add_item_view(request):
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("You do not have permission to access this page.")
    if request.method == 'POST':
        new_cd = CD.objects.create(
            title=request.POST.get('title'),
            artist=request.POST.get('artist'),
            release_year=request.POST.get('release_year'),
            genre=request.POST.get('genre'),
            description=request.POST.get('description'),
            cover_image=request.FILES.get('cover_image'),
            owner=request.user
        )
        return redirect('collection')
    return render(request, "recordstar/add_item.html")

# recordstar/views.py
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')