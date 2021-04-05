FROM registry.cn-hangzhou.aliyuncs.com/oriole/oriole:apache
MAINTAINER YourName
ENV LANG C.UTF-8
COPY html /var/www/html
COPY run.sh /tmp/run.sh
RUN chmod +x /tmp/run.sh
ENTRYPOINT cd /tmp; ./run.sh
EXPOSE 80
EXPOSE 22
