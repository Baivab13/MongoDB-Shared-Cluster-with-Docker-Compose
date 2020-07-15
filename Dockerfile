FROM python:3.6.8-alpine3.9

LABEL MAINTAINER="Shaurave Kuwar <kuwarsaurav21@gmail.com>"

WORKDIR /srv/api/

ADD ./modules /srv/api/
RUN pip install -r requirements.txt

EXPOSE 8080

CMD [ "python", "./index.py" ]