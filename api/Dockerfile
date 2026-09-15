FROM python:3.11.3-slim AS builder

WORKDIR /app

RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade --timeout 100 --retries 10 pip setuptools wheel
RUN pip install --no-cache-dir --timeout 100 --retries 10 -r requirements.txt


FROM python:3.11.3-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder /app/.venv .venv
COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]