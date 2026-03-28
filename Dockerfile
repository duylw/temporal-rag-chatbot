FROM python:3.12-alpine

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/


WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]