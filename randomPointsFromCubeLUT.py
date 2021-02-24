## Accepts a 3D LUT (in .cube format) from stdin, and returns a random subset of points from the LUT

import sys
import csv
import numpy as np

data = sys.stdin.readlines()

numSamples = int(sys.argv[1])

pointCount = 0
LUT_3D_SIZE = 0
cubeSize = 1.0

for line in csv.reader(data, delimiter=' '):
    #print(line)
    if line[0] != '#':
        if line[0] == 'LUT_3D_SIZE':
            LUT_3D_SIZE = int(line[1])
            cube = np.empty((LUT_3D_SIZE, LUT_3D_SIZE, LUT_3D_SIZE, 6), order='F')
        else:
            r = pointCount % LUT_3D_SIZE
            g = (pointCount//LUT_3D_SIZE) % LUT_3D_SIZE
            b = (pointCount//LUT_3D_SIZE**2) % LUT_3D_SIZE
            #print(f'r, g, b = {r}, {g}, {b}')

            rVal = r/LUT_3D_SIZE*cubeSize
            gVal = g/LUT_3D_SIZE*cubeSize
            bVal = b/LUT_3D_SIZE*cubeSize

            cube[r, g, b, 0] = rVal
            cube[r, g, b, 1] = gVal
            cube[r, g, b, 2] = bVal
            cube[r, g, b, 3] = float(line[0])
            cube[r, g, b, 4] = float(line[1])
            cube[r, g, b, 5] = float(line[2])
            pointCount += 1

#VALIDATE CUBE
if cube.shape[0]*cube.shape[1]*cube.shape[2] != LUT_3D_SIZE**3:
    print("ERR, cube sized incorrectly")
    exit()

print("red,green,blue,redPrime,greenPrime,bluePrime")
for i in range(numSamples):
    red = np.random.randint(LUT_3D_SIZE - 1)
    green = np.random.randint(LUT_3D_SIZE - 1)
    blue = np.random.randint(LUT_3D_SIZE - 1)
    rgbxyz = cube[red, green, blue]
    print(f'{rgbxyz[0]},{rgbxyz[1]},{rgbxyz[2]},{rgbxyz[3]},{rgbxyz[4]},{rgbxyz[5]}')
