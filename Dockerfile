FROM python:3.10-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
