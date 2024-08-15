FROM python:3.12-slim

RUN groupadd -r myuser && useradd -r -g myuser myuser && \
    mkdir -p /home/myuser/.local/share/pypoetry && \
    chown -R myuser:myuser /home/myuser

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    libmariadb-dev-compat \
    libmariadb-dev \
    curl \
    python3-dev \
    pkg-config \
    gcc \
    gunicorn && \
    rm -rf /var/lib/apt/lists/*

USER myuser

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chmod +x /home/myuser/.local/bin/poetry && \
    /home/myuser/.local/bin/poetry --version

ENV PATH="/home/myuser/.local/bin:$PATH"

WORKDIR /app

COPY . .

RUN /home/myuser/.local/bin/poetry install

EXPOSE 8000
CMD ["/home/myuser/.local/bin/poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "wallet_transaction_api.wsgi:application"]
