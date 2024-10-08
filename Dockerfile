FROM python:3.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    # pip
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore \
    # poetry
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' 

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
    apt clean && \
    rm -rf /var/cache/apt/*

COPY poetry.lock pyproject.toml /src/

WORKDIR /src

RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
    echo "$ENVIRONMENT" \
    # Install deps:
    && poetry run pip install -U pip \
    && poetry install \
    --no-interaction --no-ansi --sync 

COPY . .

RUN useradd -m -d /src -s /bin/bash app \
    && chown -R app:app /src/* && chown -R app:app /src

USER app

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000" ]
