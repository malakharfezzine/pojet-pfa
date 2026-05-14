from django import template
from gestion_stage.models import Notification
register = template.Library()
@register.simple_tag
def notif_count(user):
    if not user or not user.is_authenticated:
        return 0
    return Notification.objects.filter(destinataire=user, lu=False).count()
