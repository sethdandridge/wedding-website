FROM python:3.13.5-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache --requirement requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

RUN mkdir /app/instance

ENTRYPOINT ["gunicorn", "-w", "10", "-b", "0.0.0.0:80", "--preload", "wedding_website:create_app()"]

LABEL org.opencontainers.image.source=https://github.com/sethdandridge/wedding-website
