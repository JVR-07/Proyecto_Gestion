from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'sdc_client/home.html')
