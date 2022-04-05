FROM python:3.10-alpine

COPY ./requirements.txt /opt/qr_code/requirements.txt


RUN apk update
RUN python3 -m pip install --upgrade pip
RUN apk add zlib-dev jpeg-dev gcc musl-dev
RUN python3 -m pip install -r /opt/qr_code/requirements.txt

COPY . /opt/qr_code/
WORKDIR /opt/qr_code

RUN apk add --update nodejs npm
RUN npm i -g npx
RUN npm install

ENV FLASK_APP=qr_code

RUN chmod +x docker-entrypoint.sh

VOLUME /opt/sbank/static/
EXPOSE 8000
ENTRYPOINT ["/opt/qr_code/docker-entrypoint.sh"]
