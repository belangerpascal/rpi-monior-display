FROM python:3.9
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./
RUN python -m venv .
RUN source ./bin/activate
RUN pip install --upgrade -r requirements.txt

CMD ["python", "disp.py"]