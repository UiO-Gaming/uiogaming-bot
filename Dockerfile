FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

RUN apt update && apt install -y imagemagick ffmpeg libsm6 libxext6 graphviz

COPY . .

RUN mv /app/src/assets/misc/policy.xml /etc/ImageMagick-6/policy.xml

VOLUME logs

CMD ["python3", "src/run.py"]
