FROM python:3.14-slim
WORKDIR /handler_api

COPY /handler_api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /handler_api .

ENTRYPOINT ["python", "main.py"]