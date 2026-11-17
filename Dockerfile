FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
RUN useradd --create-home --uid 10001 appuser
USER 10001
EXPOSE 8082
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8082"]
