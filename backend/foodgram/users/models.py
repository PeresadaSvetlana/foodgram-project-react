from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN)
]


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Ник'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Пароль'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f'{self.username}: {self.email}'

    def is_admin(self):
        return self.role == self.ADMIN

