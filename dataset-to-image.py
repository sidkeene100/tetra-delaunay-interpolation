from PIL import Image
import numpy as np
import csv
import sys

BUFFERSIZE = 4096

data = sys.stdin.readlines()
filename = sys.argv[1]
image = np.zeros((BUFFERSIZE, 1, 3), dtype=np.uint8)

line_count = 0
for row in csv.reader(data, delimiter=','):
    print(row)
    if line_count == 0:
        line_count += 1
    else:
        r, g, b = float(row[0]), float(row[1]), float(row[2])
        rPrime, gPrime, bPrime = row[3], row[4], row[5]

        image[line_count - 1, 0] = [int(r*255), int(g*255), int(b*255)]
        print(f'RGB = {r*255}, {g*255}, {b*255}')

        line_count += 1

Image.fromarray(image, 'RGB').save(filename)
