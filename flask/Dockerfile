FROM python:3.7.2-stretch

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ADD . /app

CMD ["uwsgi", "app.ini"]
