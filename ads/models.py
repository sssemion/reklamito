from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Client(models.Model):
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    name = models.CharField('Название', max_length=255)
    tax_id = models.CharField('ИНН', max_length=12, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец')
    hidden = models.BooleanField('Удален', default=False)


class User2Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, db_index=True)
    role = models.CharField(max_length=50)


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
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT)
    content = models.JSONField('Контент')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
