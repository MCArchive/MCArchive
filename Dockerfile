FROM python:3.7.6-alpine

RUN apk add yarn gcc musl-dev python-dev libffi-dev postgresql-dev
RUN pip install gunicorn gevent

WORKDIR /mcarch

COPY package.json /mcarch/package.json
COPY yarn.lock /mcarch/yarn.lock

RUN yarn

COPY requirements.txt /mcarch/requirements.txt
RUN pip install -r requirements.txt

COPY webpack.config.js /mcarch/webpack.config.js
COPY assets /mcarch/assets
RUN yarn run webpack

ENV FLASK_APP mcarch
ENV MCARCH_CONFIG /mcarch/prod_config.py

COPY . /mcarch

CMD gunicorn -w 4 -k gevent -b :5000 --log-file=- "mcarch.app:create_app()"

