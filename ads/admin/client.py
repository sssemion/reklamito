from collections.abc import Callable
from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils.timezone import now

from ads.models import Campaign, Client, User2Client
from ads.permissions import check_client_permission

admin.site.unregister(Group)


class User2ClientFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        client_owner_id: int | None = None

        # Если клиент уже существует (редактирование)
        if self.instance.pk:
            client_owner_id = self.instance.owner_id
        # Если это создание нового клиента
        else:
            if self.request.user.is_superuser:
                # Для суперпользователя берем из POST-данных
                client_owner_id = self.data.get('owner')
            else:
                # Для обычных пользователей владелец = текущий пользователь
                client_owner_id = self.request.user.pk

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            user = form.cleaned_data.get('user')
            if user and user.pk == client_owner_id:
                raise ValidationError(f'Пользователь {user} является владельцем и не может быть добавлен в персонал!')


class User2ClientInline(admin.TabularInline[User2Client]):
    model = User2Client
    formset = User2ClientFormSet
    extra = 1
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Персонал'

    def get_formset(
        self, request: HttpRequest, obj: User2Client | None = None, **kwargs: Any
    ) -> type[forms.BaseInlineFormSet]:
        return super().get_formset(request, obj, **kwargs)


class CampaignInline(admin.TabularInline[Campaign]):
    model = Campaign
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ('name', 'author', 'budget', 'start_date', 'end_date', 'is_active', 'status')

    def status(self, obj: Campaign) -> str:
        today = now().date()
        if obj.start_date > today:
            return 'Запланирована'
        elif obj.end_date < today:
            return 'Завершена'
        return 'Активна'

    status.short_description = 'Статус'  # pyright: ignore[reportFunctionMemberAccess]

    def has_add_permission(self, request: HttpRequest, obj: Campaign | None = None):
        return False  # Полностью запретить добавление

    def get_queryset(self, request: HttpRequest) -> QuerySet[Campaign]:
        return super().get_queryset(request).select_related('author')


class ClientCreationForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'tax_id', 'owner')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin[Client]):
    form = ClientCreationForm
    inlines = [User2ClientInline, CampaignInline]
    list_display = ('name', 'tax_id', 'owner', 'created_at', 'hidden')
    list_filter = ('hidden', 'created_at')
    search_fields = ('name', 'tax_id')
    fields = ('name', 'tax_id', 'owner')

    def has_delete_permission(self, request: HttpRequest, obj: Client | None = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Client | None = None) -> bool:
        if request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return True
        if obj:
            return check_client_permission(
                request.user,  # pyright: ignore[reportArgumentType]
                obj,
                (User2Client.ClientStaffRoles.ADMIN,),
            )
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request: HttpRequest, obj: Client | None = None) -> bool:
        if obj:
            return check_client_permission(
                request.user,  # pyright: ignore[reportArgumentType]
                obj,
                (
                    User2Client.ClientStaffRoles.ADMIN,
                    User2Client.ClientStaffRoles.EDITOR,
                    User2Client.ClientStaffRoles.READER,
                ),
            )
        return True

    def get_formset_kwargs(
        self, request: HttpRequest, obj: Client, inline: InlineModelAdmin[Any], prefix: str
    ) -> dict[str, Any]:
        kwargs = super().get_formset_kwargs(request, obj, inline, prefix)
        if inline.model is User2Client:
            kwargs['request'] = request
        return kwargs

    def get_form(
        self, request: HttpRequest, obj: Client | None = None, change: bool = False, **kwargs: Any
    ) -> type[forms.ModelForm]:
        form = super().get_form(request, obj, change, **kwargs)
        owner: forms.ModelChoiceField | None = form.base_fields.get('owner')  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType,reportUnknownVariableType]
        if owner:
            owner.initial = request.user
            if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
                owner.queryset = User.objects.filter(pk=request.user.pk)
        return form

    def get_fields(self, request: HttpRequest, obj: Client | None = None) -> list[Callable[..., str] | str]:
        fields = list[Callable[..., str] | str](super().get_fields(request, obj))
        if request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]:
            fields.append('hidden')
        return fields

    def get_readonly_fields(self, request: HttpRequest, obj: Client | None = None) -> list[str]:
        readonly: list[str] = []
        if not request.user.is_superuser and obj is not None:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]:
            readonly += ['tax_id', 'owner']
        return readonly

    def get_queryset(self, request: HttpRequest) -> QuerySet[Client]:
        qs = super().get_queryset(request).prefetch_related('campaign_set')
        if not request.user.is_superuser:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            return (
                qs.filter(hidden=False)
                .filter(
                    Q(owner=request.user)
                    | Q(
                        user2client__user=request.user,
                    )
                )
                .distinct()
            )
        return qs
