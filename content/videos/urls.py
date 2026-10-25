from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_videos, name='list_videos'),
    path('<int:video_id>/', views.video_detail, name='video_detail'),
    path('<int:video_id>/favorite/', views.toggle_favorite_video, name='favorite_video'),
]