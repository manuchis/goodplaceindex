FROM python:3.6-alpine

RUN adduser -D goodplace

WORKDIR /home/goodplace

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY goodplace.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP goodplace.py

RUN chown -R goodplace:goodplace ./
USER goodplace

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
