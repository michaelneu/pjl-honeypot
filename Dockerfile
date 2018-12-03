FROM python:3-slim

RUN groupadd -g 1000 jetdirect && \
    useradd -r -u 1000 -g jetdirect jetdirect

RUN mkdir /app && chown -R jetdirect:jetdirect /app
USER jetdirect
COPY jetdirect.py /app/jetdirect.py
WORKDIR /app
VOLUME /app/prints
EXPOSE 9100
CMD [ "python3", "jetdirect.py", "9100", "/app/prints", "jetdirect.log" ]
