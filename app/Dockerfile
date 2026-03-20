FROM python:3.12-slim
WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

#уневирсальный запуск как на локальной машине так и в облачном
CMD sh -c "taskiq worker api.Dependencies.queue_data:broker & uvicorn main:app --host 0.0.0.0 --port $PORT"