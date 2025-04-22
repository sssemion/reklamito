from typing import Any

from django.contrib.auth import login
from django.contrib.auth.models import Permission
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from myauth.forms import StaffUserCreationForm


class SignUpView(CreateView):
    form_class = StaffUserCreationForm
    success_url = reverse_lazy('admin:index')
    template_name = 'myauth/signup.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        login(self.request, self.object)  # pyright: ignore
        permissions = Permission.objects.filter(
            codename__in=[
                'add_banner',
                'view_banner',
                'add_campaign',
                'view_campaign',
                'add_client',
                'view_client',
                'add_user2client',
                'view_user2client',
                'view_user',
            ],
            content_type__app_label__in=['ads', 'auth'],
        )
        self.object.user_permissions.add(*permissions)  # pyright: ignore
        return response
