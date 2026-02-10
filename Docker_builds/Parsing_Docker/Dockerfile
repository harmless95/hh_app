FROM python:3.14-slim
WORKDIR /app

COPY /project_parsing/requirements.txt .
# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем системные зависимости для работы браузеров (библиотеки отрисовки и т.д.)
RUN playwright install-deps chromium

# Скачиваем сам бинарник Chromium (устанавливаем только его, чтобы образ не весил 2ГБ)
RUN playwright install chromium

COPY /project_parsing .

ENTRYPOINT ["python", "main.py"]