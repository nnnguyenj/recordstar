from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib.auth.decorators import login_required
from .forms import RecordForm
from .models import Record


def index_view(request):
    return render(request, "users/index.html")

def logout_view(request):
    logout(request)
    return redirect("index")

def google_login(request):
    if request.method == 'POST':
        account_type = request.POST.get('account_type', 'P')
        request.session['account_type'] = account_type
    return oauth2_login(request)

@login_required
def dashboard_view(request):
    return render(request, "users/dashboard.html", {"user": request.user})

@login_required
def playlists_view(request):
    return render(request, "users/playlists.html")

@login_required
def recent_activity_view(request):
    return render(request, "users/recent_activity.html")

@login_required
def collection_view(request):
    records = Record.objects.filter(user=request.user)
    return render(request, "users/collection.html", {"records": records})

@login_required
def add_record_view(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user  #associate the record with the current user
            record.save()
            return redirect('collection')  #redirect to the collection page after saving
    else:
        form = RecordForm()

    return render(request, "users/add_record.html", {'form': form})

@login_required
def ratings_view(request):
    return render(request, "users/ratings.html")

@login_required
def profile_view(request):
    return render(request, "users/profile.html")

@login_required
def settings_view(request):
    return render(request, "users/settings.html")