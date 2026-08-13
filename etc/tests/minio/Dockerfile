#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

FROM golang:1.24-alpine AS build

ARG MINIO_COMMIT=07c3a429bfed433e49018cb0f78a52145d4bedeb

RUN CGO_ENABLED=0 go install github.com/minio/minio@${MINIO_COMMIT}

FROM alpine:3.22

RUN apk add --no-cache ca-certificates curl \
    && addgroup -S minio \
    && adduser -S -G minio minio \
    && mkdir /data \
    && chown minio:minio /data

COPY --from=build /go/bin/minio /usr/local/bin/minio

USER minio
VOLUME ["/data"]
EXPOSE 9000 9001

HEALTHCHECK --interval=2s --timeout=2s --start-period=5s --retries=15 \
    CMD curl --fail --silent http://127.0.0.1:9000/minio/health/live || exit 1

ENTRYPOINT ["minio"]
CMD ["server", "/data", "--address", ":9000", "--console-address", ":9001"]
