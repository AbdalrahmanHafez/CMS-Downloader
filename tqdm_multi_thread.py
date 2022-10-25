# creator: https://github.com/boydfd/tqdm_multi_thread

import io
import sys
import random
from tqdm import tqdm


TQDM_COLORS = [
    "#ff0000",
    "#00ff00",
    "#0000ff",
    "#ffff00",
    "#00ffff",
    "#ff00ff",
    "#ffffff",
    "#000000",
]

class TqdmMultiThread(io.StringIO):
    def __init__(self, texts, id,desc, total=100, lock=None):
        super().__init__()
        self.id = id
        self.lock = lock
        text = "progress #{}".format(id)
        with self.lock:
            self.texts = texts
            self.texts[id] = ''
            self.down()
        self.tqdm = tqdm(
			total=total,
			unit="B",
			unit_scale=True,
			desc=desc,
			initial=0,
			dynamic_ncols=True,
			colour=random.choice(TQDM_COLORS),
            position=id,
            file=self
        )

    def update(self, *params):
        self.tqdm.update(*params)

    def write(self, buf):
        self.with_lock_call(self._write, buf)

    def _write(self, buf):
        buf = self.strip(buf)
        if buf:
            self.texts[self.id] = buf

    @classmethod
    def strip(cls, buf):
        return buf.strip('\r\n\t\x1b[1A')

    def flush(self):
        self.with_lock_call(self._flush)

    def _flush(self):
        self.top()

        for key in sorted(self.texts):
            sys.stdout.write(self.texts[key])
            self.down()

    def up(self):
        self.print('\x1b[1A')

    def down(self):
        self.print('\n')

    def with_lock_call(self, func, *params):
        if self.lock:
            with self.lock:
                func(*params)
        else:
            func(*params)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tqdm.close()
        with self.lock:
            self.top()
            self.print(self.texts[self.id])
            self.bottom()
            del self.texts[self.id]

    def print(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def bottom(self):
        for i in range(self.get_length()):
            self.down()

    def top(self):
        for i in range(self.get_length()):
            self.up()

    def get_length(self):
        return len(self.texts)