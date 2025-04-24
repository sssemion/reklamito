FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    clang

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

ENV DJANGO_SECRET_KEY="collectstatic_only"
RUN uv run --group prod manage.py collectstatic --noinput
ENV DJANGO_SECRET_KEY=""

CMD ["uv", "run", "--group", "prod", "gunicorn", "project.wsgi:application", "--bind", "127.0.0.1:8841"]
