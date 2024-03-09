FROM python:3.9

WORKDIR /opt/app/

COPY /app/requirements.txt ./
COPY /app/disp.py ./
#RUN apk add --update alpine-sdk
RUN pip install -r requirements.txt



CMD ["python", "disp.py"]