from collections.abc import Callable
from typing import Any

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.db.models import ForeignKey, Q
from django.forms import ModelChoiceField, ModelForm
from django.http import HttpRequest

from ads.models import Banner, Campaign, Client, User2Client


class BannerInline(admin.TabularInline[Banner]):
    model = Banner
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ['name', 'is_active', 'created_at']

    def has_add_permission(self, request: HttpRequest, obj: Banner | None = None):
        return False


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin[Campaign]):
    inlines = [BannerInline]
    list_display = ('name', 'client', 'author', 'budget', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'client', 'start_date')
    search_fields = ('name', 'client__name')

    def has_change_permission(self, request: HttpRequest, obj: Campaign | None = None) -> bool:
        if request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return True
        if obj:
            if obj.client.owner == request.user:
                return True
            for u2c in User2Client.objects.filter(client=obj.client):
                if u2c.user == request.user and u2c.role in (
                    User2Client.ClientStaffRoles.ADMIN,
                    User2Client.ClientStaffRoles.EDITOR,
                ):
                    return True
        return False

    def has_view_permission(self, request: HttpRequest, obj: Campaign | None = None) -> bool:
        if request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return True
        if obj:
            if obj.client.owner == request.user:
                return True
            return request.user in obj.client.staff.all()
        return True

    def get_inlines(self, request: HttpRequest, obj: Campaign | None) -> list[type[InlineModelAdmin[Any]]]:
        if obj:
            return [BannerInline]
        return []

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request).select_related('author', 'client__owner')
        if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return qs.filter(
                Q(client__owner=request.user)
                | Q(
                    client__user2client__user=request.user,
                    client__user2client__role__in=[
                        User2Client.ClientStaffRoles.ADMIN,
                        User2Client.ClientStaffRoles.EDITOR,
                    ],
                )
            ).distinct()
        return qs

    def formfield_for_foreignkey(
        self, db_field: ForeignKey[Client], request: HttpRequest | None, **kwargs: Any
    ) -> ModelChoiceField | None:
        if db_field.name == 'client' and request:
            # Фильтруем клиентов по правам доступа
            if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
                kwargs['queryset'] = Client.objects.filter(
                    Q(owner=request.user)
                    | Q(
                        user2client__user=request.user,
                        user2client__role__in=[User2Client.ClientStaffRoles.ADMIN, User2Client.ClientStaffRoles.EDITOR],
                    )
                ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request: HttpRequest, obj: Campaign, form: ModelForm, change: bool) -> None:
        if not change:
            # Автоматически устанавливаем автора при создании
            obj.author = request.user  # pyright: ignore[reportAttributeAccessIssue]
        super().save_model(request, obj, form, change)

    def get_fields(self, request: HttpRequest, obj: Campaign | None = None) -> list[Callable[..., Any] | str]:
        fields: list[Callable[..., Any] | str] = [
            'name',
            'client',
            'budget',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at',
        ]
        if obj or request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            fields.insert(2, 'author')
        return fields

    def get_readonly_fields(self, request: HttpRequest, obj: Campaign | None = None):
        readonly = ['created_at', 'updated_at']
        if obj and not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            # Запрещаем редактирование автора и клиента после создания
            readonly += ['author', 'client']
        return readonly
