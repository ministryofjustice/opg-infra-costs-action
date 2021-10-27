FROM python:3.10.0-slim
COPY app/. .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["./main.py"]
