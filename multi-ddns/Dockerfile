ARG BUILD_FROM
FROM $BUILD_FROM

# Setup base
RUN apk add --no-cache openssl certbot

# Copy data
COPY app/*.sh /data
RUN chmod 755 /data
RUN chmod 755 /data/*.sh

WORKDIR /data
CMD [ "./run.sh" ]