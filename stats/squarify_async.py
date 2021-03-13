import time
from multiprocessing import Process, Lock

from PIL import Image

from mosaic import squarify


def f(i, lock, path):
    img = Image.open(path)
    img = squarify(img, 256)

    lock.acquire()
    try:
        img.save('test/test_1.jpg')
    finally:
        lock.release()


if __name__ == '__main__':
    start_time = time.time()

    lock = Lock()
    paths = ['test/test.jpg' for i in range(100)]

    for i, path in enumerate(paths):
        Process(target=f, args=(i, lock, path)).start()

    print("--- %s seconds ---" % (time.time() - start_time))
