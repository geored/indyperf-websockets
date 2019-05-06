FROM python:3.7
WORKDIR /opt/app
ADD . .
RUN	pip install -r requirements.txt
EXPOSE 8182
CMD ["python","server.py"]
