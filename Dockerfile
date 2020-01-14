FROM python:3.7.6-alpine

RUN apk add yarn gcc musl-dev python-dev libffi-dev postgresql-dev
RUN pip install gunicorn gevent

COPY . /mcarch
WORKDIR /mcarch

RUN yarn
RUN yarn run webpack
RUN pip install -r requirements.txt

ENV FLASK_APP mcarch
ENV MCARCH_CONFIG /mcarch/prod_config.py

CMD gunicorn -w 4 -k gevent -b :5000 --log-file=- "mcarch.app:create_app()"

