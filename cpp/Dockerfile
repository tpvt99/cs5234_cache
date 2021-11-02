FROM debian:stable-slim

ADD .. /proj

ENTRYPOINT [ "bash" ]

ENV DEBIAN_FRONTEND noninteractive

# update and install dependencies
RUN         apt-get clean \
                && apt-get update \
                && apt-get install -y --no-install-recommends linux-perf \
                && apt-get install -y \
                    software-properties-common \
                    wget \
                && apt-get update \
                && apt-get install -y \
                    make \
                    git \
                    curl \
                    vim \
                && apt-get install -y cmake \
                && apt-get install -y gcc g++