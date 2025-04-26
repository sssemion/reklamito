FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 80

RUN apt-get update && apt-get install -y \
    wget \
    nginx \
    build-essential \
    python3-dev \
    libpq-dev \
    clang

RUN mkdir -p /usr/local/share/ca-certificates/Yandex/ch && \
    wget "https://storage.yandexcloud.net/cloud-certs/RootCA.pem" \
    --output-document /usr/local/share/ca-certificates/Yandex/ch/RootCA.crt
ENV CH_SSL_CERTIFICATE_PATH=/usr/local/share/ca-certificates/Yandex/ch/RootCA.crt

RUN mkdir -p /usr/local/share/ca-certificates/Yandex/redis && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document /usr/local/share/ca-certificates/Yandex/redis/RootCA.crt
ENV REDIS_SSL_CERTIFICATE_PATH=/usr/local/share/ca-certificates/Yandex/redis/RootCA.crt

COPY project app/project
COPY ads app/ads
COPY billing app/billing
COPY experiments app/experiments
COPY myauth app/myauth
COPY templates app/templates
COPY .python-version app/python-version
COPY manage.py app/manage.py
COPY pyproject.toml app/pyproject.toml
COPY uv.lock app/uv.lock

WORKDIR /app

RUN ln -s /config/.env .env
COPY in.nginx /etc/nginx/sites-enabled/default

ENV STATIC_ROOT="/usr/share/reklamito/static"
ENV DJANGO_SECRET_KEY="collectstatic_only"
RUN uv run --group prod manage.py collectstatic --noinput
ENV DJANGO_SECRET_KEY=""

CMD service nginx restart && uv run --group prod gunicorn project.wsgi:application --bind 127.0.0.1:8841
