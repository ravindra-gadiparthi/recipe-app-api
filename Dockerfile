FROM python:3.8-alpine
MAINTAINER Ravindra GAdiparthi

ENV PYTHONUNBUFFERED 1

#copy requirements file
COPY ./requirements.txt /requirements.txt

COPY ./repositories repositories
#adding postgresql client
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

RUN adduser -D user
USER user
