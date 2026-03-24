FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /project_tg

COPY project_tg/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY project_tg/ .

ENV PYTHONPATH=/project_tg
ENTRYPOINT ["python", "main.py"]