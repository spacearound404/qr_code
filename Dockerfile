FROM python:3.10

RUN apt update && apt upgrade -y
RUN python3 -m pip install --upgrade pip
COPY . /opt/qr_code/
WORKDIR /opt/qr_code
RUN python3 -m pip install -r /opt/qr_code/requirements.txt

ENV FLASK_APP=qr_code

RUN chmod +x docker-entrypoint.sh

VOLUME /static/
EXPOSE 8000
#CMD ['python','app.py?']
#ENTRYPOINT ["/opt/qr_code/docker-entrypoint.sh"]