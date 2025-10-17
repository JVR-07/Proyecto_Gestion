from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'landing/home.html')

def personal_login(request):
    return render(request, 'login/personal_login.html')

def ong_login(request):
    return render(request, 'login/ong_login.html')

def feed(request):
    return render(request, 'posts/feed.html')

def create_post(request):
    return render(request, 'posts/create_post.html')