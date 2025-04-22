# reklamito

reklamito-publiccito - serviso for la pubblicazione reklamitos su Internet

или же курсовая работа по дисциплине "Специальные главы по базам данных"


# Описание баз данных проекта
_Все нижеприведенные пользователи имеют права только на чтение строго ограниченных ресурсов_

## Реляционные

### PostgreSQL
**Модель данных**: Реляционная + документо-ориентированная (JSONB)
**Назначение**:
- Основное хранилище данных приложения
- Пользователи, роли, настройки кампаний
- Документо-ориентированное хранение контента баннеров в формате JSONB

**Подключение**:
```
USER=reklamito-reader
PASSWORD=MpFJXZhUxUvfUrnTvBkojkwcZe3m2QLf
PORT=6432
HOST=c-gjt9xuxph9c5a02q.rw.mdb.yandexcloud.net
DATABASE=reklamito
```

### Требования безопасности
**SSL-сертификаты обязательны для всех подключений**: [Инструкция по установке сертификатов Yandex Cloud](https://yandex.cloud/ru/docs/managed-postgresql/operations/connect#get-ssl-cert)


## Колоночная аналитическая СУБД

### ClickHouse
**Модель данных**: Реляционная
**Назначение**:
- Логирование показов и кликов в реальном времени
- Аналитика эффективности рекламных кампаний
- Генерация отчетов и дашбордов

**Подключение**:
```
USER=reklamito-reader
PASSWORD=dJw53ysP6r7hZ2w9rYcTw3Kj3eZJJEEb
PORT=8443/9440
HOST=c-c9qlcsbd94m622i0iqus.rw.mdb.yandexcloud.net
DATABASE=reklamito
```

### Требования безопасности
**SSL-сертификаты обязательны для всех подключений**: [Инструкция по установке сертификатов Yandex Cloud](https://yandex.cloud/ru/docs/managed-clickhouse/operations/connect/#configure-ssl)

### Интеграция с DataLens для ClickHouse:

Используйте готовый коннектор для подключения аналитики

TBD
