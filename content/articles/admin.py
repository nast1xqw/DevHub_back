from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created')
    search_fields = ('title',)
    filter_horizontal = ('tags', 'favorites')
    
    actions = ['run_parser']

    @admin.action(description=' Спарсить статьи с Хабра')
    def run_parser(self, request, queryset):
        from .parser import parse_habr_rss
        count = parse_habr_rss()
        self.message_user(request, f'Успешно добавлено статей: {count}')