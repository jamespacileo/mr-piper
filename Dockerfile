FROM python:3.6

WORKDIR /src/app


COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pytest tests