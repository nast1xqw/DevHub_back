import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Count

from .forms import PostForm, CommentForm
from .models import Post, Comment
from users.decorators import login_required_json  

def post_to_dict(post, user=None):
    data = {
        'id': post.id,
        'title': post.title,
        'text': post.text,
        'photo': post.photo.url if post.photo else None,
        'author': {
            'id': post.author.id,
            'username': post.author.username,
            'avatar': post.author.avatar.url if getattr(post.author, 'avatar', None) else None,
        },
        'tags': list(post.tags.values_list('name', flat=True)),
        'created': post.created.isoformat(),
        'likes_count': post.likes_count,
        'comments_count': post.comments_count,
    }
    
    if user and user.is_authenticated:
        data['is_liked'] = post.likes.filter(id=user.id).exists()
        data['is_favorited'] = post.favorites.filter(id=user.id).exists()
    else:
        data['is_liked'] = False
        data['is_favorited'] = False
        
    return data

def get_data(request):
    if request.content_type == 'application/json':
        try: return json.loads(request.body)
        except ValueError: return {}
    return request.POST 

def errors_response(form):
    errors = {field: list(msgs) for field, msgs in form.errors.items()}
    return JsonResponse({'ok': False, 'errors': errors}, status=400)


@login_required_json  
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'detail': 'Метод не разрешен'}, status=405)

    form = PostForm(get_data(request), request.FILES)
    if not form.is_valid():
        return errors_response(form)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    form.save_m2m() 
    return JsonResponse({'ok': True, 'post': post_to_dict(post, request.user)}, status=201)

def list_posts(request):
    posts = Post.objects.select_related('author').prefetch_related('tags').all()
    posts_data = [post_to_dict(post, request.user) for post in posts]
    return JsonResponse({'ok': True, 'posts': posts_data})

def read_post(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('tags'), pk=post_id)
    return JsonResponse({'ok': True, 'post': post_to_dict(post, request.user)})


@login_required_json
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
        
    return JsonResponse({'ok': True, 'is_liked': is_liked, 'likes_count': post.likes_count})

@login_required_json
def toggle_favorite(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    if post.favorites.filter(id=request.user.id).exists():
        post.favorites.remove(request.user)
        is_favorited = False
    else:
        post.favorites.add(request.user)
        is_favorited = True
        
    return JsonResponse({'ok': True, 'is_favorited': is_favorited})


def list_comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author').all()
    
    data = [{
        'id': c.id,
        'text': c.text,
        'author': {'id': c.author.id, 'username': c.author.username, 'avatar': c.author.avatar.url if c.author.avatar else None},
        'created': c.created.isoformat(),
        'parent_id': c.parent_id
    } for c in comments]
    
    return JsonResponse({'ok': True, 'comments': data})

@login_required_json
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    form = CommentForm(get_data(request))
    if not form.is_valid():
        return errors_response(form)

    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    
    parent_id = get_data(request).get('parent_id')
    if parent_id:
        comment.parent = get_object_or_404(Comment, pk=parent_id, post=post)
        
    comment.save()
    return JsonResponse({'ok': True, 'comment': {'id': comment.id, 'text': comment.text}}, status=201)


def get_recommendations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': True, 'posts': []})

    favorite_tags = Post.objects.filter(favorites=request.user).values_list('tags__id', flat=True).distinct()
    
    if not favorite_tags:
        recommended = Post.objects.all()[:5]
    else:
        recommended = Post.objects.filter(tags__id__in=favorite_tags)\
            .exclude(favorites=request.user)\
            .distinct()[:10]

    posts_data = [post_to_dict(post, request.user) for post in recommended]
    return JsonResponse({'ok': True, 'posts': posts_data})