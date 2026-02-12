FROM python:3.14-slim
WORKDIR /app

RUN pip install --no-cache-dir playwright && \
    playwright install-deps chromium && \
    playwright install chromium

COPY /project_parsing/requirements.txt .
# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

COPY /project_parsing .

ENTRYPOINT ["python", "main.py"]