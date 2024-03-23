FROM python:3.9
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./
RUN python -m venv . --system-site-packages
ENV PATH="/opt/app/bin:$PATH"
RUN pip install --upgrade -r requirements.txt

CMD ["venv/bin/activate", "python", "disp.py"]
