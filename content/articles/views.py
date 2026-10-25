from django.shortcuts import render
from content.videos.views import video_to_dict  
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Article
from users.decorators import login_required_json
from content.videos.models import Video
from content.posts.models import Tag


def article_to_dict(article, user=None):
    data = {
        'id': article.id,
        'title': article.title,
        'text': article.text,
        'source_url': article.source_url,
        'tags': list(article.tags.values_list('name', flat=True)),
        'author': article.author.username if article.author else 'Админ',
        'created': article.created.strftime('%d.%m.%Y'),
    }
    if user and user.is_authenticated:
        data['is_favorited'] = article.favorites.filter(id=user.id).exists()
    else:
        data['is_favorited'] = False
    return data


def list_articles(request):
    articles = Article.objects.all()
    tag_name = request.GET.get('tag')
    if tag_name:
        articles = articles.filter(tags__name=tag_name)
    
    sort = request.GET.get('sort', 'newest')
    
    if sort == 'oldest':
        articles = articles.order_by('created')
    elif sort == 'title':
        articles = articles.order_by('title')
    else: 
        articles = articles.order_by('-created')
    
    data = [article_to_dict(article, request.user) for article in articles]
    
    return JsonResponse({'ok': True, 'articles': data})


def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return JsonResponse({'ok': True, 'article': article_to_dict(article, request.user)})


@login_required_json
def toggle_favorite_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Метод не разрешен'}, status=405)

    if article.favorites.filter(id=request.user.id).exists():
        article.favorites.remove(request.user)
        is_fav = False
    else:
        article.favorites.add(request.user)
        is_fav = True
        
    return JsonResponse({'ok': True, 'is_favorited': is_fav})


def get_recommendations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': True, 'articles': [], 'videos': []})

    fav_article_tags = Tag.objects.filter(articles__favorites=request.user).distinct()
    
    fav_video_tags = Tag.objects.filter(videos__favorites=request.user).distinct()
    
    all_tags = (fav_article_tags | fav_video_tags).distinct()

    if not all_tags:
        rec_articles = Article.objects.all()[:3]
        rec_videos = Video.objects.all()[:3]
    else:
        rec_articles = Article.objects.filter(tags__in=all_tags).exclude(favorites=request.user).distinct()[:3]
        rec_videos = Video.objects.filter(tags__in=all_tags).exclude(favorites=request.user).distinct()[:3]

    return JsonResponse({
        'ok': True,
        'articles': [article_to_dict(a, request.user) for a in rec_articles],
        'videos': [video_to_dict(v, request.user) for v in rec_videos]
    })