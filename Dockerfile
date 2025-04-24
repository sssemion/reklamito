FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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

RUN uv run manage.py collectstatic --noinput

CMD ["gunicorn", "project.wsgi:application", "--bind", "127.0.0.1:8841"]
