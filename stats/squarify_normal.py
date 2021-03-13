from PIL import Image

from mosaic import squarify

import time
start_time = time.time()

for i in range(100):
    img = Image.open('test/test.jpg')
    img = squarify(img, 256)
    img.save('test/test_1.jpg')

print("--- %s seconds ---" % (time.time() - start_time))
