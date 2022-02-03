import logging
from aws.sqs import sqs_send_message


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def chunks(lst, number):
    """
    Yield successive n-sized chunks from list (lst).
    """
    for i in enumerate(lst):
        yield lst[i:i + number]

    # for i in range(0, len(lst), number):
    #     yield lst[i:i + number]


def send(results: list, chunksize: int = 1):
    """
    Sends all results from cost explorer to the metrics service
    configured within the args (via key & uri)
    """
    length = len(results)
    chunked = list(chunks(results, chunksize))
    headers = {'x-api-key': 'XXX',
               'Content-Type': 'application/json; charset=utf-8'}

    logger.info(
        "Sending total of %s metrics in %s chunks", length, len(chunked))
    for i in range(len(chunked)):
        logger.info(f"Chunk {i}")
        data = chunked[i]
        body = {'metrics': data}
        sqs_send_message(body)
