FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
#RUN chmod +x wait-for-it.sh
#CMD ["/app/wait-for-it.sh", "influxdb_container:8086", "--", "python3", "main.py"]
CMD ["python3", "main.py"]
