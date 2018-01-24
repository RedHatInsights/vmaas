from threading import Lock


class SimpleLogger:
    """Print thread-safely input text to stdout.
    """

    def __init__(self):
        self.lock = Lock()

    def log(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()


class EnumerateLogger(SimpleLogger):
    """Print thread-safely input text to stdout. Line numbers included.
    """

    def __init__(self):
        SimpleLogger.__init__(self)
        self.i = 0

    def log(self, text="", step=1):
        self.lock.acquire()
        self.i += 1
        if text:
            print("%d: %s" % (self.i, text))
        else:
            print("%d" % self.i)
        self.lock.release()
