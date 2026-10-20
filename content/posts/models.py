from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=128,
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=1000,
    )
    photo = models.ImageField(
        verbose_name='Фото_поста',
        upload_to="posts/",
        blank=True
    )
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    ) 
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    likes = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        verbose_name='Лайки',
        related_name='liked_posts',
        blank=True,
    )
    likes_count = models.PositiveIntegerField(
        "Лайков", 
        default=0
    )
    comments_count = models.PositiveIntegerField(
        "Комментариев", 
        default=0
    )
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'posts'
        ordering = ['-created']
        verbose_name='Пост'
        verbose_name_plural='Посты'
        indexes = [
            models.Index(fields=["-created"]),
            models.Index(fields=["author", "-created"]),
        ]

class Comment(models.Model):
    post = models.ForeignKey(
        to=Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='post_comments',
    )
    text = models.TextField(
        verbose_name='Текст',
        max_length=1000,
    )
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    parent = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Родительский комментарий",
    )

    def __str__(self):
        return f'{self.author.username}: {self.text[:40]}'

    class Meta:
        db_table = 'post_comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created']