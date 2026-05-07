"""Templatelar uchun yordamchi filter va taglar."""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def status_badge(value):
    """G'oya yoki taklif statusi uchun rangli badge qaytaradi."""
    mapping = {
        'new': ('success', 'Yangi'),
        'funded': ('primary', 'Moliyalashtirilgan'),
        'closed': ('secondary', 'Yopiq'),
        'pending': ('warning', 'Kutilmoqda'),
        'accepted': ('success', 'Qabul qilingan'),
        'rejected': ('danger', 'Rad etilgan'),
    }
    color, label = mapping.get(value, ('secondary', value))
    return mark_safe(f'<span class="badge bg-{color}">{label}</span>')


@register.filter
def som(value):
    """So'm formatida ko'rsatish: 1 000 000 so'm."""
    try:
        v = int(value)
        return f"{v:,}".replace(",", " ") + " so'm"
    except (TypeError, ValueError):
        return value


@register.simple_tag
def query_transform(request, **kwargs):
    """Joriy GET-paramlarni saqlab qolib, ba'zilarini almashtiradi (filtr, sahifalar uchun foydali)."""
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is None or v == '':
            updated.pop(k, None)
        else:
            updated[k] = v
    return updated.urlencode()
