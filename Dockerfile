FROM python:3.13

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.1.1
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

COPY . /app

CMD ["python", "run.py"]
