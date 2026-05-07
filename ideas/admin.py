from django.contrib import admin

from .models import Idea, Offer, SavedIdea, Message


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'industry', 'region', 'needed_amount',
                    'status', 'created_at')
    list_filter = ('status', 'industry', 'region')
    search_fields = ('title', 'short_description', 'description', 'author__username')
    date_hierarchy = 'created_at'


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('idea', 'investor', 'amount', 'equity_percent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('idea__title', 'investor__username')


@admin.register(SavedIdea)
class SavedIdeaAdmin(admin.ModelAdmin):
    list_display = ('user', 'idea', 'created_at')
    search_fields = ('user__username', 'idea__title')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('offer', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('content', 'sender__username')
