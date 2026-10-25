from django.db import models
from django.conf import settings
from content.posts.models import Tag


class Video(models.Model):
    title = models.CharField('Название видео', max_length=200)
    description = models.TextField('Описание', blank=True)
    video_url = models.URLField('Ссылка на видео')
    
    tags = models.ManyToManyField(Tag, verbose_name='Теги', blank=True, related_name='videos')
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        verbose_name='В избранном', 
        blank=True, 
        related_name='favorite_videos'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='Автор'
    )
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'videos'
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        ordering = ['-created']