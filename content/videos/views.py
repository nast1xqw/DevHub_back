from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Video
from users.decorators import login_required_json


def video_to_dict(video, user=None):
    data = {
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'video_url': video.video_url,
        'tags': list(video.tags.values_list('name', flat=True)),
        'author': video.author.username if video.author else 'Админ',
        'created': video.created.strftime('%d.%m.%Y'),
    }
    if user and user.is_authenticated:
        data['is_favorited'] = video.favorites.filter(id=user.id).exists()
    else:
        data['is_favorited'] = False
    return data


def list_videos(request):
    """Список видео с фильтрацией и сортировкой"""
    videos = Video.objects.all()
    
    tag_name = request.GET.get('tag')
    if tag_name:
        videos = videos.filter(tags__name=tag_name)
    
    sort = request.GET.get('sort', 'newest')
    
    if sort == 'oldest':
        videos = videos.order_by('created')
    elif sort == 'title':
        videos = videos.order_by('title')
    else:
        videos = videos.order_by('-created')
    
    data = [video_to_dict(video, request.user) for video in videos]
    return JsonResponse({'ok': True, 'videos': data})


def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return JsonResponse({'ok': True, 'video': video_to_dict(video, request.user)})


@login_required_json
def toggle_favorite_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Метод не разрешен'}, status=405)

    if video.favorites.filter(id=request.user.id).exists():
        video.favorites.remove(request.user)
        is_fav = False
    else:
        video.favorites.add(request.user)
        is_fav = True
        
    return JsonResponse({'ok': True, 'is_favorited': is_fav})