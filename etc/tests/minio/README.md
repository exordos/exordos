# MinIO backup test server

Build and start an isolated S3-compatible server for manual backup tests:

```shell
docker build -t exordos-test-minio -f etc/tests/minio/Dockerfile .
docker run --rm --name exordos-test-minio \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER="$MINIO_ROOT_USER" \
  -e MINIO_ROOT_PASSWORD="$MINIO_ROOT_PASSWORD" \
  exordos-test-minio
```

Set both credentials in the shell before running the container. Use
`http://127.0.0.1:9000` as `endpoint_url` in the S3 backup configuration. Create
the configured bucket before running `exordos backup`; the MinIO console is at
`http://127.0.0.1:9001`.

This image is for tests only. It builds the pinned MinIO release from source and
does not contain credentials or create buckets automatically.
