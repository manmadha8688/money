from .models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.active_user
        except Profile.DoesNotExist:
            profile = None
    else:
        profile = None
    return {'profile': profile}
