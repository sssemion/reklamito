from typing import Any

from django.contrib.auth.models import User
from django.db import models


class Client(models.Model):
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    name = models.CharField('Название', max_length=255)
    tax_id = models.CharField('ИНН', max_length=12, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец', related_name='owned_clients')
    staff = models.ManyToManyField[User, 'User2Client'](User, through='User2Client', related_name='member_of')
    hidden = models.BooleanField('Удален', default=False)

    def __str__(self) -> str:
        return self.name


class User2Client(models.Model):
    class Meta:
        unique_together = ('user', 'client')

    class ClientStaffRoles(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        EDITOR = 'editor', 'Редактор'
        READER = 'reader', 'Читатель'

    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, db_index=True)
    role = models.CharField('Роль', max_length=20, choices=ClientStaffRoles, default=ClientStaffRoles.READER)


class Campaign(models.Model):
    class Meta:
        verbose_name = 'Кампания'
        verbose_name_plural = 'Кампании'

    name = models.CharField('Название', max_length=255)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    budget = models.DecimalField('Бюджет (₽)', max_digits=10, decimal_places=2)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)


class Banner(models.Model):
    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    name = models.CharField('Служебное название', max_length=255)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name='banners')
    content = models.JSONField[dict[str, Any]]('Контент')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
