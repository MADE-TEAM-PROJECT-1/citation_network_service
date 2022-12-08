FROM python:3.8-slim-buster

WORKDIR /classification_inference

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENV MODEL_LINK "https://drive.google.com/file/d/1nYNUqcjxdDjlAsF3VWqRQJtKYiIGM1OY/view?usp=share_link"
RUN mkdir models
COPY app/ ./app
