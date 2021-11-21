# coding: utf-8
# from multiprocessing.sharedctypes import synchronized
import random
import time

from watchmen.config.config import settings


class InvalidSystemClock(Exception):
    pass


WORKER_ID_BITS = 5
DATACENTER_ID_BITS = 5
SEQUENCE_BITS = 12

MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 2**5-1 0b11111
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)

#
WOKER_ID_SHIFT = SEQUENCE_BITS
DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

#
MAX_SEQUENCE = -1 ^ (-1 << SEQUENCE_BITS)

TWEPOCH = 1420041600000


class IdWorker(object):
    """
    generate ids
    """

    def __init__(self, datacenter_id, worker_id, sequence=0):
        """
        init
        :param datacenter_id: data center id
        :param worker_id: machine id
        :param sequence: sequence id
        """
        # sanity check
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError('worker_id max value')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError('datacenter_id max value')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

        self.last_timestamp = -1  #

    def _gen_timestamp(self):
        """
        generate a timestamp
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def get_id(self):
        """
        get a new id
        :return:
        """
        timestamp = self._gen_timestamp()

        #
        if timestamp < self.last_timestamp:
            raise InvalidSystemClock

        if timestamp == self.last_timestamp:
            # randomness = random.SystemRandom().getrandbits(12)
            # print(randomness)
            # self.sequence = randomness
            self.sequence = (self.sequence + 1) & MAX_SEQUENCE
            if self.sequence == 0:
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
                 (self.worker_id << WOKER_ID_SHIFT) | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        next timestamp id
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


worker = IdWorker(settings.SNOWFLAKE_DATACENTER, settings.SNOWFLAKE_WORKER)


def get_surrogate_key():
    return str(worker.get_id())


def get_int_surrogate_key():
    return worker.get_id()


if __name__ == '__main__':
    worker = IdWorker(0, 0)
    # print(worker.get_id())
