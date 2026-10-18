from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("Email", unique=True)
    patronymic = models.CharField("Отчество", max_length=150, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    bio = models.CharField("О себе", max_length=300, blank=True)

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(part for part in parts if part)

    def avatar_url(self):
        return self.avatar.url if self.avatar else None