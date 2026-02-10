FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade wheel "poetry==2.2.1"

RUN poetry config virtualenvs.create false

COPY project_tg/pyproject.toml project_tg/poetry.lock ./

RUN poetry install

COPY /project_tg .

ENTRYPOINT ["python", "main.py"]