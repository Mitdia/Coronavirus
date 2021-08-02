# Coronavirus


# DEV

```bash
docker-compose build
docker-compose up
```

# flask Dockerfile

FROM python:3.7.2-stretch

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ADD . /app

CMD ["uwsgi", "app.ini"]


# nginx Dockerfile

FROM nginx

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/

# nginx.conf

server {
	listen 80;
	listen [::]:80;

  location / {
      include uwsgi_params;
      uwsgi_pass flask:8080;
  }
}


# docker-compose.yml
version: "3.7"
services:

  flask:
    build: ./flask
    container_name: flask
    restart: always
    environment:
      - APP_NAME=MyFlaskApp
    expose:
      - 8080

  nginx:
    build: ./nginx
    container_name: nginx
    restart: always
    ports:
      - "80:80"
