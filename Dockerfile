FROM python:3.10-slim

WORKDIR /app

ARG poetryargs="--only main"
ARG GID=1001
ARG UID=1001
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install poetry

RUN addgroup --gid $GID --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid $UID --system --group app

COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false && \
    poetry install ${poetryargs} --no-interaction --no-ansi

COPY --chown=app gas_calculator /app/gas_calculator/

USER app
