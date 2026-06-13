FROM python:3.11.3 AS builder

WORKDIR /app

RUN python -m venv .venv

COPY requirements.txt .

# Aumenta o timeout para evitar que a rede caia no builder remoto
RUN .venv/bin/python -m pip install --upgrade --timeout 100 --retries 10 pip setuptools wheel

# Instala sem cache para economizar memória e com persistência de rede
RUN .venv/bin/pip install --no-cache-dir --timeout 100 --retries 10 -r requirements.txt

FROM python:3.11.3-slim

WORKDIR /app

# Copia o ambiente virtual e o resto dos arquivos do projeto
COPY --from=builder /app/.venv .venv
COPY . .

CMD ["/app/.venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]