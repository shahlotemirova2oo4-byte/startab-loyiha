"""Template context processorlari."""
from .models import Message


def unread_messages_count(request):
    if not request.user.is_authenticated:
        return {'unread_messages_count': 0}

    if request.user.is_startup:
        count = Message.objects.filter(
            offer__idea__author=request.user, is_read=False,
        ).exclude(sender=request.user).count()
    elif request.user.is_investor:
        count = Message.objects.filter(
            offer__investor=request.user, is_read=False,
        ).exclude(sender=request.user).count()
    else:
        count = 0

    return {'unread_messages_count': count}
