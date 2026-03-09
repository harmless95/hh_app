FROM python:3.12-slim
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Для локального тестирования
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Для облачного запуска
#CMD taskiq worker api.Dependencies.queue_data:broker & uvicorn main:app --host 0.0.0.0 --port $PORT