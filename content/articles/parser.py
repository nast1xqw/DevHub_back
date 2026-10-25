import feedparser
from django.contrib.auth import get_user_model
from .models import Article
from content.posts.models import Tag

User = get_user_model()

def parse_habr_rss():
    url = "https://habr.com/ru/hub/programming/rss/"
    feed = feedparser.parse(url)
    
    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        return 0
        
    count = 0
    tag, _ = Tag.objects.get_or_create(name='Программирование')

    for entry in feed.entries[:5]:
        if not Article.objects.filter(source_url=entry.link).exists():
            article = Article.objects.create(
                title=entry.title,
                text=entry.get('summary', 'Нет описания'),
                source_url=entry.link,
                author=admin
            )
            article.tags.add(tag)
            count += 1
            
    return count