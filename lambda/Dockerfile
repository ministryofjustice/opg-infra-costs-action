FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task
COPY ./costs-to-metrics ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["daily.handler"]
