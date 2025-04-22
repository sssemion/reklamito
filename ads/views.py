import uuid
from typing import Any
from urllib.parse import urlencode

import httpagentparser  # pyright: ignore
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now

from ads.ch import CH_CLIENT, ClickHouseWriteError, DeviceType
from ads.models import Banner


def _get_client_ip(request: HttpRequest) -> str | None:
    """Получение IP клиента с учетом прокси"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def _parse_user_agent(user_agent: str) -> dict[str, Any]:
    """Парсинг User-Agent (упрощенная версия)"""
    data = httpagentparser.detect(user_agent)  # pyright: ignore
    return {
        'browser_family': data.get('browser', {}).get('name'),
        'browser_version': data.get('browser', {}).get('version'),
        'os_family': data.get('os', {}).get('name'),
        'device_type': DeviceType.mobile if 'Mobile' in user_agent else DeviceType.desktop,
    }


def show_banner(request: HttpRequest, banner_id: int) -> HttpResponse:
    banner = get_object_or_404(Banner, pk=banner_id, is_active=True)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    client_ip = _get_client_ip(request)
    show_uuid = uuid.uuid4()
    timestamp = now()

    ua_info = _parse_user_agent(user_agent)

    try:
        CH_CLIENT.log_show(
            event_id=show_uuid,
            timestamp=timestamp,
            banner_id=banner.pk,
            campaign_id=banner.campaign_id,  # pyright: ignore
            user_id=request.user.pk if request.user.is_authenticated else None,
            ip_address=client_ip,
            user_agent=user_agent,
            **ua_info
        )
    except ClickHouseWriteError:
        if settings.DEBUG:
            raise

    show_time = timestamp.timestamp()

    click_params: dict[str, Any] = {
        'show_uuid': show_uuid,
        'show_time': show_time,
    }

    html = render_to_string(
        'ads/banner.html',
        {'banner': banner, 'click_url': reverse('click', args=[banner.pk]) + '?' + urlencode(click_params)},
    )

    return HttpResponse(html)


def handle_click(request: HttpRequest, banner_id: int) -> HttpResponse:
    banner = get_object_or_404(Banner, pk=banner_id, is_active=True)

    show_uuid = request.GET.get('show_uuid')
    show_time = float(request.GET.get('show_time', 0))

    if show_uuid is None:
        raise Http404()

    click_time = now()
    time_to_click = (click_time.timestamp() - show_time) if show_time else None

    # Логируем клик
    try:
        CH_CLIENT.log_click(
            show_event_id=uuid.UUID(show_uuid),
            timestamp=click_time,
            banner_id=banner.pk,
            campaign_id=banner.campaign_id,  # pyright: ignore
            time_to_click=time_to_click,
            referer_url=request.META.get('HTTP_REFERER'),
        )
    except ClickHouseWriteError:
        if settings.DEBUG:
            raise

    return redirect(banner.click_url)
