FROM python:3.9-slim
EXPOSE 8000
WORKDIR /mysite/
COPY requirements.txt .
RUN apt update
RUN apt install mysql-client 
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./mysite/ .
COPY ./mysite.env 
COPY ./mysite.service /etc/init.d/

COPY shell.sh .
RUN chmod +x shell.sh
CMD ["./shell.sh"]
