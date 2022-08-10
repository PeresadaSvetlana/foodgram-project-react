from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254, blank=False, unique=True, verbose_name="Почта"
    )
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Ник"
    )
    first_name = models.CharField(
        max_length=150, blank=True, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150, blank=True, verbose_name="Фамилия"
    )
    password = models.CharField(
        max_length=150, blank=True, verbose_name="Пароль"
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.username}: {self.email}"


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower", blank=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscribe"
            )
        ]
