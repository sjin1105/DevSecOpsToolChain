FROM python:3.9-slim
WORKDIR /mysite/
COPY requirements.txt .
RUN apt update
RUN apt install python-dev libmariadb-dev gcc -y
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./mysite/ .
COPY ./nginx-mysite /etc/nginx/sites-available/nginx-mysite
RUN ln -s /etc/nginx/sites-available/nginx-mysite /etc/nginx/sites-enabled/
COPY shell.bash .
RUN chmod +x shell.bash
CMD ["./shell.bash"]
