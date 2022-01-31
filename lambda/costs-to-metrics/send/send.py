import pprint
from aws.sqs import send_message

pp = pprint.PrettyPrinter(indent=4).pprint


def chunks(lst, n):
    """
    Yield successive n-sized chunks from list (lst).
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def send(results: list, chunksize: int = 20):
    """
    Sends all results from cost explorer to the metrics service
    configured within the args (via key & uri)
    """
    length = len(results)
    chunked = list(chunks(results, chunksize))
    headers = {'x-api-key': 'XXX',
               'Content-Type': 'application/json; charset=utf-8'}

    print(f"Sending total of [{length}] metrics in [{len(chunked)}] chunks")
    for i in range(len(chunked)):
        print(f"Chunk {i}")
        data = chunked[i]
        body = {'metrics': data}
        send_message(body)
