from django.db import models
from django.conf import settings
from content.posts.models import Tag


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст статьи')
    source_url = models.URLField('Ссылка на источник', blank=True, null=True)
    
    tags = models.ManyToManyField(Tag, verbose_name='Теги', blank=True, related_name='articles')
    
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        verbose_name='В избранном', 
        blank=True, 
        related_name='favorite_articles'
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
        db_table = 'articles'
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created']