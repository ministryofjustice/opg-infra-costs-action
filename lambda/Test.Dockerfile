FROM public.ecr.aws/lambda/python:3.8

RUN pip install requests requests_aws4auth

WORKDIR /var/task
COPY ./costs-to-metrics ./
CMD ["daily.handler"]
