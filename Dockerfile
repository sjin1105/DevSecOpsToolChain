FROM python:3.9-alpine3.17
EXPOSE 8000
WORKDIR /mysite/
COPY requirements.txt .
RUN apk update
RUN apk add gcc musl-dev mariadb-connector-c-dev 
RUN pip3 install -r requirements.txt --no-cache-dir
RUN apk del gcc musl-dev

COPY ./mysite/ .
COPY ./mysite.env /
COPY ./mysite.service /etc/init.d/

COPY shell.sh .
RUN chmod +x shell.sh
CMD ["./shell.sh"]
