FROM python:3.10.1-slim
COPY app/. .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["./main.py"]
