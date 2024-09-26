FROM python:3.12.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
