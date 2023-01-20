FROM python:3.9-slim
EXPOSE 8000
WORKDIR /mysite/
COPY requirements.txt .
RUN apt update
RUN apt install python-dev libmariadb-dev gcc -y
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./mysite/ .

COPY shell.bash .
RUN chmod +x shell.bash
CMD ["./shell.bash"]
