FROM python:3.7.3-slim
COPY requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN apt update
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 libasound2.dev vim ffmpeg exiftool
COPY . /app
RUN chmod 755 /app
RUN chmod 755 /app/*.sh
RUN chmod 755 /app/*.py
WORKDIR /app
ENTRYPOINT ["sh /app/gunicorn_starter_speaker.sh"]
