FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

RUN apt update && apt install -y imagemagick ffmpeg libsm6 libxext6

COPY . .

RUN mv /app/src/assets/misc/policy.xml /etc/ImageMagick-6/policy.xml

CMD ["python3", "src/run.py"]
