from django import forms
from content.posts.models import Tag
from .models import Article


class ArticleForm(forms.ModelForm):
    tags_input = forms.CharField(required=False)

    class Meta:
        model = Article
        fields = ['title', 'text', 'source_url']

    def save_tags(self, article):
        names = [n.strip() for n in self.cleaned_data.get('tags_input', '').split(',') if n.strip()]
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            article.tags.add(tag)