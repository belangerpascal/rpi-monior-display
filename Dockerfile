FROM python:3.11
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/* ./
RUN python -m venv . --system-site-packages
ENV PATH="/opt/app/bin:$PATH"
RUN pip install --upgrade -r requirements.txt

CMD ["python", "disp.py"]
