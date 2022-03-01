FROM python:3.7.3-slim
COPY requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN apt update
RUN apt-get install -y  vim 
COPY . /app
RUN chmod 755 /app
RUN chmod 755 /app/*.sh
RUN chmod 755 /app/*.py
WORKDIR /app
CMD ["./gunicorn_start_kobo_dash.sh"]
