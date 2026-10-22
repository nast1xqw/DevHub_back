from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_posts, name='posts-list'),
    path('create/', views.create_post, name='posts-create'),
    path('<int:post_id>/', views.read_post, name='posts-detail'),
    path('<int:post_id>/like/', views.toggle_like, name='posts-like'),
    path('<int:post_id>/favorite/', views.toggle_favorite, name='posts-favorite'),
    path('<int:post_id>/comments/', views.list_comments, name='comments-list'),
    path('<int:post_id>/comments/create/', views.create_comment, name='comments-create'),
    path('recommendations/', views.get_recommendations, name='posts-recommendations'),
]