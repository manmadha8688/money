from django.shortcuts import render, redirect
from .models import Profile

def myprofile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Check if only profile picture is being updated
        if 'profile_picture' in request.FILES:
            profile.company_logo = request.FILES['profile_picture']
            profile.save()
            return redirect('myprofile')
 
        # Check if other details are being updated
        else:
            profile.name = request.POST.get('name', profile.name)
            profile.email = request.POST.get('email', profile.email)
            profile.phone = request.POST.get('phone_number', profile.phone)
            profile.company_name = request.POST.get('company_name', profile.company_name)
            profile.email = request.POST.get('company_email', profile.email)
            profile.tagline = request.POST.get('tagline', profile.tagline)
            profile.bio = request.POST.get('bio', profile.bio)
            profile.company_interest = request.POST.get('company_interest', profile.company_interest)
            profile.save()
            return redirect('myprofile')

    return render(request, 'lender/myprofile.html', {'profile': profile})
