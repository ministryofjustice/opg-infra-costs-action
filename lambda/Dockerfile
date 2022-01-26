FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task
COPY ./costs-to-metrics ./
CMD ["daily.handler"]
