# creator: https://github.com/boydfd/tqdm_multi_thread

import threading

from tqdm_multi_thread import TqdmMultiThread


class TqdmMultiThreadFactory:
    def __init__(self):
        self.texts = {}
        self.lock = threading.Lock()

    def create(self, id,desc, total):
        return TqdmMultiThread(self.texts, id, desc, total, self.lock)