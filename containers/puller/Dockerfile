FROM golang:alpine

LABEL version = "0.1" \
      author = "Kamil Tokmakov" \
      organization = "HLRS" \
      description = "An extension for contrib/download-frozen-image-v2.sh of the Moby Project. \
      It uses client certificate for authentication in private docker registry"

ENV DOCKER_REGISTRY="154.48.185.207"
ENV DOCKER_IMAGES_DST="/images"
ENV DOCKER_CLIENT_CERT="/certs"

RUN apk update && \
    apk add curl jq bash --no-cache

COPY ./pull.sh /

WORKDIR /

ENTRYPOINT ["/pull.sh"]