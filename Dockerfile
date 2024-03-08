FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY controller/requirements.txt ./
RUN pip install --index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt

COPY controller .

CMD ["python", "controller.py"]
