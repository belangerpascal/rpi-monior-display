FROM python:3.11
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/* ./
RUN apt update
RUN apt install -y gpiod python3-libgpiod
#RUN python -m venv . --system-site-packages
RUN python -m venv .
ENV PATH="/opt/app/bin:$PATH"
#ENV GPIOZERO_PIN_FACTORY=lgpio
RUN pip install --upgrade -r requirements.txt
RUN cp /usr/lib/python3/dist-packages/gpiod.*.so ./lib/python3.11/site-packages/gpiod.so

CMD ["python", "disp.py"]
