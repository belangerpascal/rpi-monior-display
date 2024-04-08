FROM python:3.11
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/* ./
RUN apt update
RUN apt install -y gpiod libgpiod2
#RUN python -m venv . --system-site-packages
RUN python -m venv .
ENV PATH="/opt/app/bin:$PATH"
#ENV GPIOZERO_PIN_FACTORY=lgpio
RUN pip install --upgrade -r requirements.txt

CMD ["python", "disp.py"]
