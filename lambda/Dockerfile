FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task
COPY ./costs_to_metrics ./
CMD ["daily.handler"]
