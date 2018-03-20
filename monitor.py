import argparse
import logging
import os
import signal
import time
from queue import Queue
from pprint import pprint
from threading import Lock
from threading import Thread

import tldextract
import yaml
from certstream.core import CertStreamClient
from requests.adapters import HTTPAdapter
from termcolor import cprint

ARGS = argparse.Namespace()
CONFIG = yaml.safe_load(open("config.yaml"))
KEYWORDS = [line.strip() for line in open("keywords.txt")]
S3_URL = "http://s3-1-w.amazonaws.com"
BUCKET_HOST = "%s.s3.amazonaws.com"
QUEUE_SIZE = CONFIG['queue_size']
UPDATE_INTERVAL = CONFIG['update_interval']  # seconds
RATE_LIMIT_SLEEP = CONFIG['rate_limit_sleep']  # seconds

FOUND_COUNT = 0


class CertStreamThread(Thread):
    def __init__(self, q, *args, **kwargs):
        self.q = q
        self.c = CertStreamClient(
            self.process, skip_heartbeats=True, on_open=None, on_error=None)

        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            cprint("Waiting for Certstream events - this could take a few minutes to queue up...",
                   "yellow", attrs=["bold"])
            self.c.run_forever()
            time.sleep(10)

    def process(self, message, context):
        if message["message_type"] == "heartbeat":
            return

        if message["message_type"] == "certificate_update":
            self.q.put(message['data'])


class MessageQueue(Queue):
    def __init__(self, maxsize):
        self.lock = Lock()
        self.checked_buckets = list()
        self.rate_limited = False
        self.next_yield = 0

        super().__init__(maxsize)

    def put(self, bucket_url):
        if bucket_url not in self.checked_buckets:
            self.checked_buckets.append(bucket_url)
            super().put(bucket_url)

    def get(self):
        with self.lock:
            t = time.monotonic()
            if self.rate_limited and t < self.next_yield:
                time.sleep(self.next_yield - t)
                t = time.monotonic()
                self.rate_limited = False

            self.next_yield = t + RATE_LIMIT_SLEEP

        return super().get()


class MessageProcessor(Thread):
    def __init__(self, q, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = q

    def run(self):
        while True:
            try:
                certificate_update = self.q.get()
                all_domains = certificate_update["leaf_cert"]["all_domains"]
                print(all_domains)

                # pprint(certificate_update)
                # print(message['data']['not_after'])
            except Exception as e:
                print(e)
                pass
            finally:
                self.q.task_done()


def main():
    parser = argparse.ArgumentParser(description="Follow certificate update messages from CertStrea",
                                     usage="python bucket-stream.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--threads", metavar="", type=int, dest="threads", default=5,
                        help="Number of threads to spawn. More threads = more power. Limited to 5 threads if unauthenticated.")

    parser.parse_args(namespace=ARGS)
    logging.disable(logging.WARNING)

    if not CONFIG["aws_access_key"] or not CONFIG["aws_secret"]:
        cprint("It is highly recommended to enter AWS keys in config.yaml otherwise you will be severely rate limited!"
               "You might want to run with --ignore-rate-limiting", "red")

        if ARGS.threads > 5:
            cprint(
                "No AWS keys, reducing threads to 5 to help with rate limiting.", "red")
            ARGS.threads = 5

    threads = list()

    try:
        q = MessageQueue(maxsize=QUEUE_SIZE)
        threads.extend([CertStreamThread(q)])
        threads.extend([MessageProcessor(q) for _ in range(0, ARGS.threads)])
        [t.start() for t in threads]

        signal.pause()  # pause the main thread
    except KeyboardInterrupt:
        cprint("Quitting - waiting for threads to finish up...",
               "yellow", attrs=["bold"])
        [t.join() for t in threads]


if __name__ == "__main__":
    main()
