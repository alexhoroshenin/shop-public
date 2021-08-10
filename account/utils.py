from .models import Profile


def get_profile(user):
    """Возвращает профиль пользователя или one"""
    if user and user.is_authenticated:
        profiles = Profile.objects.filter(user=user)
        if profiles:
            return profiles[0]
    return None


def get_user_from_request(request):
    if request.user.is_authenticated:
        return request.user
    return None
