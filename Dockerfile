FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP=microblog.py

ENV DATABASE_URL=mysql+pymysql://microblog:123@127.0.0.1:3306/microblog

EXPOSE 5000
RUN pip install gunicorn pymysql cryptography

ENTRYPOINT ["./boot.sh"]

