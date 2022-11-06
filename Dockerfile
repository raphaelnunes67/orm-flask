FROM python:3.9.5

WORKDIR /home

COPY requirements.txt ./

RUN apt-get update && apt-get upgrade -y

RUN apt-get install nginx -y

RUN pip3 install -r requirements.txt

COPY app.py ./

COPY blocklist.py ./

COPY sql_alchemy.py ./

COPY wsgi.py ./

ADD data data

ADD models models

ADD resources resources

ADD scripts scripts

ADD settings settings

ADD tests tests

RUN FLASK_APP=wsgi.py

RUN rm /etc/nginx/sites-enabled/default

COPY ./conf/flask_settings.conf /etc/nginx/sites-enabled

RUN /etc/init.d/nginx restart

EXPOSE 5000