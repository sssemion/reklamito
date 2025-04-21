from typing import Any

from django.contrib import admin
from django.db.models import Q, QuerySet
from django.http import HttpRequest

from ads.models import Campaign, Client, User2Client


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'author', 'budget', 'is_active')
    list_filter = ('name', 'client', 'author', 'is_active', 'start_date')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Campaign]:
        qs = super().get_queryset(request)
        if not request.user.is_superuser:  # type: ignore[attr-defined]
            owner_q = Q(client__owner=request.user)
            staff_q = Q(client_id__in=User2Client.objects.filter(user=request.user).values_list('client_id', flat=True))
            return qs.filter(owner_q | staff_q)
        return qs


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_filter = ('name', 'owner')
    readonly_fields = ('tax_id', 'hidden')

    def get_readonly_fields(self, request: HttpRequest, obj: Client | None = None) -> list[str] | tuple[Any, ...]:
        ro_fields = super().get_readonly_fields(request, obj)
        if obj is not None and not (request.user.is_superuser or obj.owner == request.user):  # type: ignore[attr-defined]
            return [*ro_fields, 'owner']
        return ro_fields

    def get_queryset(self, request: HttpRequest) -> QuerySet[Client]:
        qs = super().get_queryset(request)
        return qs.filter(hidden=False)
