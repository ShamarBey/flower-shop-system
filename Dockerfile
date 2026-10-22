FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
RUN python -m venv /opt/venv

# Этот слой переиспользуется, пока не меняются зависимости.
COPY requirements.txt ./
RUN /opt/venv/bin/python -m pip install -r requirements.txt

COPY pyproject.toml ./
COPY src/ ./src/
RUN /opt/venv/bin/python -m pip install --no-deps .


FROM python:3.13-slim AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HTTP_HOST=0.0.0.0 \
    HTTP_PORT=8000 \
    APP_ENV=production

WORKDIR /app
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv
USER 10001:10001

EXPOSE 8000

# Только стандартная библиотека: curl и дополнительные пакеты не нужны.
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import json, os, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('HTTP_PORT', '8000') + '/api/v1/health', timeout=3); assert r.status == 200 and json.load(r)['status'] == 'pass'"]

CMD ["python", "-m", "flower_shop"]
