FROM python:2.7

WORKDIR /src/app


COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN python tests/test_piper.py