from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.create_room),
    path('rooms/<str:code>/join/', views.join_room),
    path('rooms/<str:code>/movies/', views.add_movie),
    path("rooms/<str:code>/start/", views.start_tournament),
    path("rooms/<str:code>/current-match/", views.current_match),
    path("rooms/<str:code>/vote/", views.vote),
]