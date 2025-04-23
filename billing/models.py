from decimal import Decimal
from typing import Any

from django.core.validators import MinValueValidator
from django.db import models

from ads.models import Client


class Invoice(models.Model):
    INVOICE_STATUS = (
        ('draft', 'Черновик'),
        ('issued', 'Выставлен'),
        ('paid', 'Оплачен'),
        ('canceled', 'Отменен'),
        ('refunded', 'Возвращен'),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Клиент'
    )
    number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Номер счета'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Сумма'
    )
    status = models.CharField(
        max_length=10,
        choices=INVOICE_STATUS,
        default='draft',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    due_date = models.DateField(verbose_name='Срок оплаты')
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата оплаты'
    )
    campaign = models.ForeignKey(
        'ads.Campaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Рекламная кампания'
    )
    metadata = models.JSONField[dict[str, Any]](
        default=dict,
        blank=True,
        verbose_name='Метаданные'
    )

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['due_date']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Счет #{self.number} ({self.client})"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('bank_card', 'Банковская карта'),
        ('yoomoney', 'ЮMoney'),
        ('sbp', 'СБП'),
        ('invoice', 'Платежное поручение'),
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Счет'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма платежа'
    )
    method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name='Способ оплаты'
    )
    processed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата обработки'
    )
    external_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Внешний ID платежа'
    )
    is_refund = models.BooleanField(
        default=False,
        verbose_name='Возврат средств'
    )
    receipt_url = models.URLField(
        blank=True,
        verbose_name='Ссылка на чек'
    )
    details = models.JSONField[dict[str, Any]](
        default=dict,
        blank=True,
        verbose_name='Детали платежа'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-processed_at']


class ClientBalance(models.Model):
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='balance',
        verbose_name='Клиент'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.0'),
        verbose_name='Текущий баланс'
    )
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.0'),
        verbose_name='Кредитный лимит'
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление'
    )

    class Meta:
        verbose_name = 'Баланс клиента'
        verbose_name_plural = 'Балансы клиентов'

    def __str__(self):
        return f"Баланс {self.client}: {self.amount}"
