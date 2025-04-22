from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Dict, Iterable, Optional, cast
from uuid import UUID

from clickhouse_driver import Client  # pyright: ignore
from django.conf import settings
from django.utils.functional import LazyObject, cached_property


class DeviceType(StrEnum):
    mobile = 'mobile'
    desktop = 'desktop'
    tablet = 'tablet'


class CostModel(StrEnum):
    CPM = 'CPM'
    CPC = 'CPC'


class NetworkType(StrEnum):
    wifi = 'wifi'
    cellular = 'cellular'
    wired = 'wired'


class ButtonType(StrEnum):
    text = 'text'
    image = 'image'
    video = 'video'


class ClickHouseWriteError(Exception):
    """Кастомное исключение для ошибок записи"""


class CHClient:
    @cached_property
    def _client(self) -> Client:
        ssl: dict[str, Any] = {}
        if settings.CH_SSL_CERTIFICATE_PATH:
            ssl |= {
                'secure': True,
                'verify': True,
                'ca_certs': settings.CH_SSL_CERTIFICATE_PATH,
            }
        return Client(
            database=settings.CH_DATABASE,
            port=settings.CH_PORT,
            user=settings.CH_USER,
            password=settings.CH_PASSWORD,
            host=settings.CH_HOST,
            **ssl,
        )

    def log_show(
        self,
        event_id: UUID,
        timestamp: datetime,
        banner_id: int,
        campaign_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        device_type: Optional[DeviceType] = None,
        os_family: Optional[str] = None,
        os_version: Optional[str] = None,
        browser_family: Optional[str] = None,
        browser_version: Optional[str] = None,
        screen_width: Optional[int] = None,
        screen_height: Optional[int] = None,
        language: Optional[str] = None,
        referer_domain: Optional[str] = None,
        referer_path: Optional[str] = None,
        is_robot: Optional[bool] = None,
        ad_position: Optional[str] = None,
        ad_size: Optional[str] = None,
        cost_model: Optional[CostModel] = None,
        session_id: Optional[str] = None,
        network_type: Optional[NetworkType] = None,
        connection_speed: Optional[int] = None,
    ) -> None:
        """Логирование показа баннера"""
        data = locals()
        data.pop('self')
        if data['is_robot'] is not None:
            data['is_robot'] = int(data['is_robot'])
        self._execute_insert(table='reklamito.shows', data=data, columns=data.keys())

    def log_click(
        self,
        show_event_id: UUID,
        timestamp: datetime,
        banner_id: int,
        campaign_id: int,
        click_x: Optional[int] = None,
        click_y: Optional[int] = None,
        element_id: Optional[str] = None,
        element_class: Optional[str] = None,
        referer_url: Optional[str] = None,
        http_method: Optional[str] = None,
        form_data: Optional[str] = None,
        time_to_click: Optional[float] = None,
        is_conversion: Optional[bool] = None,
        conversion_value: Optional[Decimal] = None,
        click_cost: Optional[Decimal] = None,
        button_type: Optional[ButtonType] = None,
        click_depth: Optional[int] = None,
        scroll_position: Optional[int] = None,
        hover_time: Optional[float] = None,
    ) -> None:
        """Логирование клика"""
        data = locals()
        data.pop('self')
        if data['is_conversion'] is not None:
            data['is_conversion'] = int(data['is_conversion'])

        self._execute_insert(table='reklamito.clicks', data=data, columns=data.keys())

    def _execute_insert(self, table: str, data: Dict[str, Any], columns: Iterable[str]) -> None:
        """Выполнение INSERT запроса"""
        try:
            self._client.execute(f'INSERT INTO {table} ({", ".join(columns)}) VALUES', [data])  # pyright: ignore
        except Exception as e:
            raise ClickHouseWriteError(f'Failed to insert into {table}: {str(e)}') from e


class LazyCHCLient(LazyObject):
    def _setup(self) -> None:
        self._wrapped = CHClient()


CH_CLIENT = cast(CHClient, LazyCHCLient())
