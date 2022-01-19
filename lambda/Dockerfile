FROM public.ecr.aws/lambda/python:3.9

WORKDIR /var/task
COPY ./costs ./
CMD ["daily.handler"]
