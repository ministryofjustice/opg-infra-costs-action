import os
import pprint
from aws.sqs import sqs_send_message

pp = pprint.PrettyPrinter(indent=4).pprint


def chunks(lst, n):
    """
    Yield successive n-sized chunks from list (lst).
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def send(results: list):
    """
    Sends all results from cost explorer to the metrics service
    configured within the args (via key & uri)
    """
    chunksize = os.getenv(int('CHUNK_SIZE'), 20)
    length = len(results)
    chunked = list(chunks(results, chunksize))
    headers = {'x-api-key': 'XXX',
               'Content-Type': 'application/json; charset=utf-8'}

    print(f"Sending total of [{length}] metrics in [{len(chunked)}] chunks")
    for i in range(len(chunked)):
        print(f"Chunk {i}")
        data = chunked[i]
        body = {'metrics': data}
        sqs_send_message(body)
