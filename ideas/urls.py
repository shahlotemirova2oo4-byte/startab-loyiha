from django.urls import path
from . import views

app_name = 'ideas'

urlpatterns = [
    path('', views.home, name='home'),

    # Ideas
    path('ideas/', views.idea_list, name='list'),
    path('ideas/new/', views.idea_create, name='create'),
    path('ideas/my/', views.my_ideas, name='my_ideas'),
    path('ideas/<int:pk>/', views.idea_detail, name='detail'),
    path('ideas/<int:pk>/edit/', views.idea_edit, name='edit'),
    path('ideas/<int:pk>/delete/', views.idea_delete, name='delete'),

    # Offers
    path('ideas/<int:idea_pk>/offer/', views.offer_create, name='offer_create'),
    path('offers/my/', views.my_offers, name='my_offers'),
    path('offers/received/', views.received_offers, name='received_offers'),
    path('offers/<int:pk>/accept/', views.offer_accept, name='offer_accept'),
    path('offers/<int:pk>/reject/', views.offer_reject, name='offer_reject'),

    # Saved
    path('ideas/<int:idea_pk>/save/', views.toggle_save, name='toggle_save'),
    path('saved/', views.saved_ideas, name='saved'),

    # Messaging
    path('chat/<int:pk>/', views.offer_chat, name='offer_chat'),
    path('inbox/', views.inbox, name='inbox'),
]
