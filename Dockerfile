FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN apk upgrade --no-cache \
    && pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
RUN adduser -D -u 10001 appuser
USER 10001
EXPOSE 8082
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8082"]
