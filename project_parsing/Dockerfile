FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir playwright && \
    playwright install-deps chromium && \
    playwright install chromium

COPY ./requirements.txt .
# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]