from django.contrib import admin
from .models import Comment, Post, Tag 


@admin.register(Tag)  
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'likes_count', 'comments_count', 'created')
    search_fields = ('title', 'text')
    readonly_fields = ('likes_count', 'comments_count')
    filter_horizontal = ('tags', 'favorites', 'likes')  


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'text', 'created')
    search_fields = ('text',)