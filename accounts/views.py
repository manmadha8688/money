from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages
def register(request):
    if request.method == "POST":
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return redirect(f"{reverse('register')}?error=password_mismatch")

        if User.objects.filter(username=username).exists():
            return redirect(f"{reverse('register')}?error=username_taken")

        if User.objects.filter(email=email).exists():
            return redirect(f"{reverse('register')}?error=email_taken")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = name
        user.save()
        return redirect(f"{reverse('login')}?registered=true")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember', False)

        user = authenticate(request, username=username, password=password)

        if user is not None :
            if user.last_name != "":
                return redirect(f"{reverse('login')}?user=borrower")
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect("/?login=success")
        else:
            return redirect(f"{reverse('login')}?error=invalid")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect(f"{reverse('login')}?logout=true")

def client_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember', False)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.last_name == "":
                return redirect(f"{reverse('client-login')}?user=false")
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            if user.last_name == "true":
                return redirect('change-client-password')  # create this URL/view
            else:
                messages.success(request,'Welcome back, '+user.first_name)
                return redirect('client-dashboard')
        else:
            return redirect(f"{reverse('client-login')}?error=invalid")

    return render(request, "accounts/client_login.html")

def client_logout_view(request):
    logout(request)
    return redirect(f"{reverse('client-login')}?logout=true")