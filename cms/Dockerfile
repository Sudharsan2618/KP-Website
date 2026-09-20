FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=kp_cms.settings.production

RUN useradd --create-home --shell /usr/sbin/nologin kp \
    && mkdir -p /app/static /app/media \
    && chown -R kp:kp /app

WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=kp:kp . /app
USER kp

EXPOSE 8000
CMD ["gunicorn", "kp_cms.wsgi:application", "--bind", "0.0.0.0:8000"]
