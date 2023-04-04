FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    postgresql-client \
    supervisor \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install wheel
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app
COPY configs/blob.conf /etc/nginx/conf.d/default.conf
COPY configs/supervisor.conf /etc/supervisor/conf.d/

EXPOSE 80
#enable at production
#CMD ["sh", "-c", "daphne -b 0.0.0.0 -p 8000 blob.asgi:application & nginx -g 'daemon off;'"]
CMD ["hupper", "-m", "manage"]
