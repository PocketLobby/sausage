"""
Consumer designed to read from constituent votes from SQS queue
"""

from vote_tallies.constituent_vote import ConstituentVoteCreator
from utilities.configurator import Configurator
import boto3
import json
import logging
import sys

def get_messages_from_queue(fx):
    """
    Get messages off SQS queue and call function with message

    NOTEST

    :param fx: a function to call with each message
    :return:
    """
    config = Configurator().config
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=config['constituent_vote_sqs_queue'])
    for msg in queue.receive_messages():
        fx(msg)


def process_message(msg, processor_klass=ConstituentVoteCreator):
    """
    process SQS messages. Messages processing functions are presumed to be idempotent

    """

    logging.info(msg.body)
    votes = json.loads(msg.body)

    ts = votes['timestamp']
    ut = votes['user_token']

    successful_commits = 0

    for bill_opinion in votes['bill_opinions']:
        cvc = processor_klass(ut, ts, bill_opinion['bill_id'], bill_opinion['vote'])

        # NOTE: it occasionally happens where the sausage user's db is not in sync
        # with our mailing list. The pipeline hasn't been wired up yet
        # Later, these should get added to an error queue in SQS
        if not cvc.constituent_id:
            logging.error("Constituent %s NOT YET CREATED IN DB" % ut)
            break

        if cvc.commit_user_vote():
            successful_commits += 1

    # NOTE: need a better way to report errors. I keep my eye on the console for now
    if successful_commits == len(votes['bill_opinions']):
        logging.debug("success! %s" % cvc)
        msg.delete()
    else:
        logging.error("Not all messages saved. MSG: %s" % votes)


def main():
    logging.info("starting queue consumer")
    while True:
        get_messages_from_queue(process_message)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main()
