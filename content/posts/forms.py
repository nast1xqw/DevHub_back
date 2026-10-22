from django import forms
from .models import Comment, Post, Tag

MAX_PHOTO = 2 * 1024 * 1024

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False, 
        label='Теги (через запятую)',
        help_text='Например: python, django, react'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'photo']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size') and photo.size > MAX_PHOTO:
            raise forms.ValidationError('Файл больше 2 МБ')
        return photo

    def save(self, commit=True):
        post = super().save(commit=commit)
        
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)
                
        return post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']