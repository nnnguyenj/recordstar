from django.shortcuts import render
from django.http import HttpResponse

# SHERRIFF: very basic index page created
def index(request):
    return HttpResponse("This now has a failed test.")
# Create your views here.
