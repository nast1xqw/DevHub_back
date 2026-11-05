from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_articles, name='list_articles'),
    path('create/', views.create_article, name='create_article'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('favorites/', views.get_favorites, name='favorites'),
    path('parse/', views.parse_articles_api, name='articles-parse'),
    path('<int:article_id>/', views.article_detail, name='article_detail'),
    path('<int:article_id>/favorite/', views.toggle_favorite_article, name='favorite_article'),
    path('<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('<int:article_id>/delete/', views.delete_article, name='delete_article'),
]