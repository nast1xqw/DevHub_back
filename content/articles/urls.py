from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_articles, name='list_articles'),
    path('recommendations/', views.get_recommendations, name='recommendations'),  
    path('<int:article_id>/', views.article_detail, name='article_detail'),  
    path('<int:article_id>/favorite/', views.toggle_favorite_article, name='favorite_article'),
]