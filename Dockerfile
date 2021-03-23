FROM python:3.8-alpine
MAINTAINER Ravindra GAdiparthi

ENV PYTHONUNBUFFERED 1

#copy requirements file
COPY ./requirements.txt /requirements.txt

COPY ./repositories repositories
#adding postgresql client
RUN apk add --update --no-cache postgresql-client jpeg-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main

RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user
