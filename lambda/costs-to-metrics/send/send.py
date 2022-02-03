import logging
from aws.sqs import sqs_send_message


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def chunks(lst, number):
    """
    Yield successive n-sized chunks from list (lst).
    """

    for i in range(0, len(lst), number):
        yield lst[i:i + number]


def send(results: list, chunksize: int = 1):
    """
    Sends all results from cost explorer to the metrics service
    configured within the args (via key & uri)
    """
    length = len(results)
    chunked = list(chunks(results, chunksize))

    logger.info(
        "Sending total of %s metrics in %s chunks", length, len(chunked))

    for i in range(len(chunked)):
        logger.info("Chunk %s", i)
        data = chunked[i]
        body = {'metrics': data}
        sqs_send_message(body)
