from decimal import Decimal
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ads.models import Banner, Campaign


class Experiment(models.Model):
    EXPERIMENT_TYPES = (
        ('banner_design', 'Дизайн баннера'),
        ('cta_button', 'Текст кнопки'),
        ('pricing', 'Ценовая стратегия'),
        ('targeting', 'Таргетинг'),
        ('placement', 'Размещение'),
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Название эксперимента'
    )
    experiment_type = models.CharField(
        max_length=20,
        choices=EXPERIMENT_TYPES,
        verbose_name='Тип эксперимента'
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='experiments',
        verbose_name='Рекламная кампания'
    )
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный эксперимент'
    )
    target_metric = models.CharField(
        max_length=50,
        default='ctr',
        verbose_name='Целевая метрика',
        help_text="Метрика для оценки эффективности (CTR, конверсии и т.д.)"
    )
    min_sample_size = models.PositiveIntegerField(
        default=1000,
        verbose_name='Минимальный размер выборки',
        help_text="Минимальный размер выборки для статистической значимости"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Эксперимент'
        verbose_name_plural = 'Эксперименты'
        ordering = ['-start_date']



class Variant(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name='Эксперимент'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название варианта'
    )
    weight = models.PositiveSmallIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Вес варианта (%)',
        help_text="Вес варианта в процентах"
    )
    is_control = models.BooleanField(
        default=False,
        verbose_name='Контрольная группа',
        help_text="Является ли вариант контрольной группой"
    )
    config = models.JSONField[dict[str, Any]](
        verbose_name='Конфигурация',
        help_text="Конфигурация варианта (зависит от типа эксперимента)"
    )
    banner = models.ForeignKey(
        Banner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанный баннер',
        help_text="Связанный баннер (для экспериментов с баннерами)"
    )

    class Meta:
        verbose_name = 'Вариант эксперимента'
        verbose_name_plural = 'Варианты экспериментов'
        unique_together = ('experiment', 'name')

    def __str__(self):
        return f"{self.experiment}: {self.name}"


class ExperimentResult(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Эксперимент'
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Вариант'
    )
    date = models.DateField(verbose_name='Дата')
    impressions = models.PositiveIntegerField(
        default=0,
        verbose_name='Показы'
    )
    clicks = models.PositiveIntegerField(
        default=0,
        verbose_name='Клики'
    )
    conversions = models.PositiveIntegerField(
        default=0,
        verbose_name='Конверсии'
    )
    spend = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.0'),
        verbose_name='Затраты'
    )
    metadata = models.JSONField[dict[str, Any]](
        default=dict,
        blank=True,
        verbose_name='Дополнительные данные'
    )

    class Meta:
        verbose_name = 'Результат эксперимента'
        verbose_name_plural = 'Результаты экспериментов'
        unique_together = ('experiment', 'variant', 'date')
        ordering = ['date']

    @property
    def ctr(self):
        return (self.clicks / self.impressions) * 100 if self.impressions else 0


class TargetingGroup(models.Model):
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='targeting_groups',
        verbose_name='Эксперимент'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название группы'
    )
    criteria = models.JSONField[dict[str, Any]](
        verbose_name='Критерии таргетинга',
        help_text="Критерии таргетинга (гео, устройства, интересы и т.д.)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активная группа'
    )

    class Meta:
        verbose_name = 'Группа таргетинга'
        verbose_name_plural = 'Группы таргетинга'

    def __str__(self):
        return f"{self.experiment}: {self.name}"
