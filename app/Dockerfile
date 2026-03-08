FROM python:3.12-slim
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD taskiq worker api.Dependencies.queue_data:broker & uvicorn main:app --host 0.0.0.0 --port $PORT