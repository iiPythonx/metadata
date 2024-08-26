# Copyright (c) 2024 iiPython

# Modules
from threading import Thread
from queue import Queue, Empty
from typing import Callable, Iterable

# Good base for multithreading
# Not sure I'll keep using this, but it works
def multithread(items: Iterable, callback: Callable, *args) -> None:
    queue = Queue()
    [queue.put(item) for item in items]

    # Handle callback
    def setup_callback(queue: Queue) -> None:
        while True:
            try:
                callback(queue.get(False), *args)

            except Empty:
                break

    # Launch threads
    threads = []
    for _ in range(4):
        threads.append(Thread(target = setup_callback, args = (queue,)))
        threads[-1].start()

    [thread.join() for thread in threads]
