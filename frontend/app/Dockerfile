FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && yes | unminimize

# install the required packges and remove caches
RUN apt-get update \
    && apt-get install -y \
        git \
        wget \
        curl \
        sudo \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        default-jdk \
        default-jre \
        scala \
        man-db \
        shellcheck \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev \
        libsasl2-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN mkdir /root/.nvm

# nvm environment variables
ENV NVM_DIR /root/.nvm
ENV NODE_VERSION 22.5.1

RUN \
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

WORKDIR /app

COPY . .

RUN  . ~/.nvm/nvm.sh \
    && nvm install $NODE_VERSION \
    && npm ci \
    && npm run build

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

EXPOSE 3000

CMD ["npm","start"]