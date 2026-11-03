import feedparser
import bleach
from django.contrib.auth import get_user_model
from .models import Article
from content.posts.models import Tag

User = get_user_model()

# Разрешённые HTML-теги (безопасные)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'blockquote', 'code', 'pre']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt'],
}

def clean_html(html_text):
    """Очищает HTML от опасных тегов и скриптов"""
    if not html_text:
        return ''
    # Удаляем все теги кроме разрешённых
    cleaned = bleach.clean(html_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return cleaned

def parse_habr_rss():
    urls = [
        "https://habr.com/ru/hub/programming/rss/",
        "https://habr.com/ru/rss/best/daily/",
        "https://habr.com/ru/rss/articles/",
    ]
    
    feed = None
    for url in urls:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
            feed = feedparser.parse(xml_data)
            if feed.entries:
                break
        except Exception as e:
            print(f"Ошибка с {url}: {e}")
            continue
    
    if not feed or not feed.entries:
        return 0
    
    admin = User.objects.filter(is_staff=True).first()
    if not admin:
        return 0
    
    count = 0
    tag, _ = Tag.objects.get_or_create(name='Программирование')
    
    for entry in feed.entries[:10]:
        if not Article.objects.filter(source_url=entry.link).exists():
            # Получаем HTML-контент
            html_content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
            
            # Очищаем HTML
            clean_text = clean_html(html_content)
            
            article = Article.objects.create(
                title=entry.title,
                text=clean_text,  # ← теперь чистый HTML
                source_url=entry.link,
                author=admin
            )
            article.tags.add(tag)
            count += 1
            print(f"✅ Добавлена: {entry.title}")
    
    print(f"📊 Всего добавлено: {count}")
    return count