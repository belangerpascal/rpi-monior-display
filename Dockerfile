FROM python:3.9-ubuntu

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./
RUN apk add --no-cache make
RUN pip install -r requirements.txt



CMD ["python", "disp.py"]