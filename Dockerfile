FROM ubuntu:26.04

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

ARG CACHE_BUST=1

RUN curl -fsSL https://repo.exordos.com/install.sh > install.sh \
    && chmod +x install.sh \
    && ./install.sh
