from typing import Any

from django import forms
from django.contrib import admin
from django.db.models import ForeignKey, Q, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_json_widget.widgets import JSONEditorWidget  # pyright: ignore[reportMissingTypeStubs]

from ads.models import Banner, Campaign, User2Client
from ads.permissions import check_client_permission
from ads.redis import REDIS_CLIENT


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'
        widgets: dict[str, Any] = {'content': JSONEditorWidget(mode='code', options={'modes': ['code', 'form']})}


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin[Banner]):
    form = BannerForm
    list_display = ('name', 'campaign', 'client_info', 'is_active', 'created_at')
    list_filter = ('is_active', 'campaign__client')
    search_fields = ('name', 'campaign__name')
    readonly_fields = ('created_at',)
    list_select_related = ('campaign__client',)

    def client_info(self, obj: Banner) -> str:
        return f'{obj.campaign.client.name} ({obj.campaign.client.tax_id})'

    client_info.short_description = 'Клиент'  # pyright: ignore[reportFunctionMemberAccess]

    def has_change_permission(self, request: HttpRequest, obj: Banner | None = None) -> bool:
        if request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return True
        if obj:
            return check_client_permission(
                request.user,  # pyright: ignore[reportArgumentType]
                obj.campaign.client,
                (User2Client.ClientStaffRoles.ADMIN, User2Client.ClientStaffRoles.EDITOR),
            )
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request: HttpRequest, obj: Banner | None = None) -> bool:
        if obj:
            return check_client_permission(
                request.user,  # pyright: ignore[reportArgumentType]
                obj.campaign.client,
                (
                    User2Client.ClientStaffRoles.ADMIN,
                    User2Client.ClientStaffRoles.EDITOR,
                    User2Client.ClientStaffRoles.READER,
                ),
            )
        return True

    def get_queryset(self, request: HttpRequest) -> QuerySet[Banner]:
        qs = super().get_queryset(request).select_related('campaign__client__owner')
        if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return qs.filter(
                Q(campaign__client__owner=request.user)
                | Q(
                    campaign__client__user2client__user=request.user,
                    campaign__client__user2client__role__in=[
                        User2Client.ClientStaffRoles.ADMIN,
                        User2Client.ClientStaffRoles.EDITOR,
                        User2Client.ClientStaffRoles.READER,
                    ],
                )
            ).distinct()
        return qs

    def formfield_for_foreignkey(self, db_field: ForeignKey[Any], request: HttpRequest | None, **kwargs: Any) -> forms.ModelChoiceField | None:
        if request and db_field.name == 'campaign':
            if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
                kwargs['queryset'] = Campaign.objects.filter(
                    Q(client__owner=request.user)
                    | Q(
                        client__user2client__user=request.user,
                        client__user2client__role__in=[
                            User2Client.ClientStaffRoles.ADMIN,
                            User2Client.ClientStaffRoles.EDITOR,
                        ],
                    )
                ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def clicks(self, obj: Banner) -> int | None:
        return REDIS_CLIENT.get_clicks(obj.pk)

    def shows(self, obj: Banner) -> int | None:
        return REDIS_CLIENT.get_shows(obj.pk)

    def show_url(self, obj: Banner) -> str | None:
        url = reverse('show_banner', args=[obj.pk])
        return mark_safe(f'<a href="{url}">Ссылка на встраиваемый баннер</a>')

    show_url.allow_tags = True

    def get_readonly_fields(self, request: HttpRequest, obj: Banner | None = None):
        readonly = ['created_at', 'clicks', 'shows', 'show_url']
        if obj and not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            readonly.append('campaign')
        return readonly
