# vim:set ft=dockerfile:
FROM ubuntu:jammy
ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-ec"]

RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    build-essential \
    git \
    zlib1g-dev \
    lsb-release \
    software-properties-common \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libffi-dev \
    liblzma-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# See https://github.com/tianon/docker-brew-debian/issues/49 for discussion of the following
#
# https://bugs.debian.org/830696 (apt uses gpgv by default in newer releases, rather than gpg)
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
    && echo 'export PATH="/root/.pyenv/bin:$PATH"' >> /root/.bashrc \
    && echo 'eval "$(pyenv init -)"' >> /root/.bashrc 


ENV PATH="$PATH:/root/.pyenv/bin:/root/.pyenv/shims"
ENV PYENV_ROOT="/root/.pyenv"

RUN pyenv install 3.7 && pyenv install 3.8 && pyenv install 3.9 && pyenv install 3.10 && pyenv install 3.11 && pyenv global 3.11

WORKDIR /root
