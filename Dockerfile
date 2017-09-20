FROM python:2.7

WORKDIR /src/app

# RUN pip install -U piper
# COPY piper.json piper.json
# COPY piper.lock piper.lock
# RUN piper install
COPY ./requirements ./requirements
RUN pip install -r requirements/dev-locked.txt

COPY . .
RUN pip install -e .
RUN python tests/test_piper.py
