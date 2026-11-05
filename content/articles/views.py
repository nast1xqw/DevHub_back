import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Article
from users.decorators import login_required_json, staff_required_json
from content.posts.models import Tag
from .forms import ArticleForm
from .parser import parse_habr_rss


@staff_required_json
def create_article(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    
    try:
        data = json.loads(request.body)
    except ValueError:
        data = {}
    
    form = ArticleForm(data)
    if not form.is_valid():
        errors = {f: list(m) for f, m in form.errors.items()}
        return JsonResponse({'ok': False, 'errors': errors}, status=400)
    
    article = form.save(commit=False)
    article.author = request.user
    article.save()
    form.save_tags(article)
    
    return JsonResponse({'ok': True, 'article': article_to_dict(article, request.user)}, status=201)


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


@login_required_json
def get_favorites(request):
    favorite_articles = Article.objects.filter(favorites=request.user).order_by('-created')
    data = [article_to_dict(article, request.user) for article in favorite_articles]
    return JsonResponse({'ok': True, 'articles': data})


@staff_required_json
def edit_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    
    try:
        data = json.loads(request.body)
    except ValueError:
        data = {}
    
    form = ArticleForm(data, instance=article)
    if not form.is_valid():
        errors = {f: list(m) for f, m in form.errors.items()}
        return JsonResponse({'ok': False, 'errors': errors}, status=400)
    
    form.save()
    form.save_tags(article)
    
    return JsonResponse({'ok': True, 'article': article_to_dict(article, request.user)})


@staff_required_json
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    
    if request.method != 'DELETE':
        return JsonResponse({'ok': False}, status=405)
    
    article.delete()
    return JsonResponse({'ok': True})


def get_recommendations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': True, 'articles': []})
    
    fav_article_tags = Tag.objects.filter(articles__favorites=request.user).distinct()
    
    if not fav_article_tags:
        rec_articles = Article.objects.all()[:3]
    else:
        rec_articles = Article.objects.filter(tags__in=fav_article_tags)\
            .exclude(favorites=request.user).distinct()[:3]
    
    return JsonResponse({
        'ok': True,
        'articles': [article_to_dict(a, request.user) for a in rec_articles]
    })
    
@staff_required_json
def parse_articles_api(request):
    
    count = parse_habr_rss()
    
    if count > 0:
        return JsonResponse({
            'ok': True, 
            'message': f'Успешно добавлено статей: {count}',
            'count': count
        })
    else:
        return JsonResponse({
            'ok': True, 
            'message': 'Новые статьи не найдены или все уже добавлены',
            'count': 0
        })