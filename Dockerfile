FROM python:3.9
LABEL org.opencontainers.image.source https://github.com/belangerpascal/rpi-monitor-display

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./
RUN python -m venv .
ENV PATH="/opt/app/bin:$PATH"
RUN pip install --upgrade -r requirements.txt

CMD ["python", "disp.py"]