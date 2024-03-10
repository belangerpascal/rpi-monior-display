FROM python:3.9
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./

RUN apk add --update alpine-sdk
RUN pip install --upgrade -r requirements.txt
RUN pip3 install --upgrade adafruit-python-shell
RUN wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
RUN PATH=$PATH python3 raspi-blinka.py

CMD ["python", "disp.py"]