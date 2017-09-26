FROM randomknowledge/docker-pyenv-tox

WORKDIR /src/app

RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
RUN pyenv update

RUN apt-get -y install libncurses5 libncurses5-dev libncursesw5


# RUN pyenv install 2.7.14
# RUN pyenv install 3.6.2
# RUN pyenv install 3.7-dev
# RUN pyenv install pypy-dev
# RUN pyenv install pypy3-dev

RUN pyenv global 2.7.13 3.1.5 3.6.1
RUN pyenv local 3.6.1
RUN pip install pytest
RUN pip install piper
# pypy-dev pypy3-dev

# RUN pip install -U piper
# COPY piper.json piper.json
# COPY piper.lock piper.lock
# RUN piper install
COPY ./requirements ./requirements
# COPY ./wheelhouse ./wheelhouse
# RUN piper install
# RUN pip install -r requirements/dev-locked.txt
# RUN pip install --no-index --find-links=./wheelhouse -r requirements/dev-locked.txt

COPY . .
RUN pip install -e .
# RUN python tests/test_piper.py

# CMD python tests
