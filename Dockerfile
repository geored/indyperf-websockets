FROM python:3.7
WORKDIR /opt/app
ADD . .
RUN	pip install -r requirements.txt
EXPOSE 8888
CMD ["python","app.py"]
