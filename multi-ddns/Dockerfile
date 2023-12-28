ARG BUILD_FROM
FROM $BUILD_FROM

# Setup base
RUN apk add --no-cache openssl certbot

# Copy data
COPY app/*.sh /
RUN chmod 755 /*.sh

CMD [ "/run.sh" ]