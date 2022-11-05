FROM python:3.9.5

WORKDIR /home

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY app.py ./

COPY blacklist.py ./

COPY sql_alchemy.py ./

ADD data data

ADD models models

ADD resources resources

ADD scripts scripts

ADD settings settings

ADD tests tests

CMD python3 app.py

EXPOSE 8000

