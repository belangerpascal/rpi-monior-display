FROM python:3.9-alpine

WORKDIR /usr/src/app/

COPY disp/requirements.txt ./
COPY disp/disp.py ./
RUN pip install --index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt



CMD ["python", "disp.py"]