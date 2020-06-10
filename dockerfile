# FROM selenium/standalone-firefox
# # FROM python:3.7
#
#
# # # install google chrome
# # RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# # RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# # RUN apt-get -y update
# # RUN apt-get install -y google-chrome-stable
# #
# # # install chromedriver
# # RUN apt-get install -yqq unzip
# # RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# # RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# #
# # # set display port to avoid crash
# # ENV DISPLAY=:99
# #
# #
# # # RUN pip install -e .
# RUN sudo apt-get update && sudo apt-get install -y \
#     python3 \
#     python3-pip \
#     libpq-dev
#
# RUN pip3 install numpy
#
# COPY setup.py /
# COPY requirements.txt /
# COPY run.py /
FROM python:3.7.5-alpine


# CMD sudo python3 run.py --browser headless

# pull official base image

# Get all the prereqs

# And of course we need Firefox if we actually want to *use* GeckoDriver

# Then install GeckoDriver
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub
RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.31-r0/glibc-2.31-r0.apk
RUn apk add glibc-2.31-r0.apk
RUN apk add --no-cache \
    autoconf \
    automake \
    bash \
    g++ \
    postgresql-dev \
    nasm \
    firefox-esr \
    gcc \
    libxslt-dev \
    jpeg-dev \
    zlib-dev \
    xvfb \
    dbus
RUN rm  -rf /tmp/* /var/cache/apk/* &&\
    wget "https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz" &&\
    tar -xvf geckodriver-v0.24.0-linux64.tar.gz &&\
    rm -rf geckodriver-v0.24.0-linux64.tar.gz &&\
    chmod a+x geckodriver &&\
    mv geckodriver /usr/local/bin/

WORKDIR /home/
# install dependencies


COPY setup.py /home/
COPY requirements.txt /home/
COPY run.py /home/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install PyVirtualDisplay
# copy project
# COPY . /usr/src/app/

