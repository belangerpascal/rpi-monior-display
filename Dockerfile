FROM python:3.9-alpine

WORKDIR /usr/src/app/

COPY /usr/src/app/disp/requirements.txt ./
COPY /usr/src/app/disp/disp.py ./
RUN pip install -r requirements.txt



CMD ["python", "disp.py"]