FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN apt update
RUN apt install -y software-properties-common
RUN apt install -y python3-launchpadlib
RUN add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt update
RUN apt install -y ffmpeg
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
