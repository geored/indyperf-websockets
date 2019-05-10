FROM python:3.6-slim
WORKDIR /opt/app
ADD . .
RUN	pip install -r requirements.txt
CMD ["python","client.async.py"]
