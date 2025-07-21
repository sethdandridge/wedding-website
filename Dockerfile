FROM python:3.13.5-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache --requirement requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

# WORKDIR /app/wedding_website

# ENV PYTHONPATH=/app/wedding_website

ENTRYPOINT ["gunicorn", "-w", "5", "-b", "0.0.0.0:80", "wedding_website:create_app()"]

LABEL org.opencontainers.image.source=https://github.com/sethdandridge/wedding-website
