import numpy as np
from scipy.spatial import Delaunay
import math
import csv

nv = np.array([-1.0, -1.0, -1.0])

#TODO: proper gamut mapping
#add documentation
#R and B are getting swapped *somewhere*

def isInvalid(point):
    if point[0] == nv[0] or point[1] == nv[1] or point[2] == nv[2]:
        return True
    return False

def tessellate(points): #tessellate an array of points, shape: np.array([[0, 0, 0], [0, 1.1, 0], [1, 0, 0], [1, 1, 0]])
    return Delaunay(points)

def keypointLookup(rgb):
    return np.asarray(keypointDict[rgb[0], rgb[1], rgb[2]])

def barycentricCoordinates(r, r1, r2, r3, r4):
    lambda1 = lambda2 = lambda3 = lambda4 = 0
    T = np.matrix([[ r1[0]-r4[0], r2[0]-r4[0], r3[0]-r4[0] ],
                   [ r1[1]-r4[1], r2[1]-r4[1], r3[1]-r4[1] ],
                   [ r1[2]-r4[2], r2[2]-r4[2], r3[2]-r4[2] ]])
    T_inv = np.linalg.inv(T)
    lambdas = np.dot(T_inv, (r - r4))
    lambda1 = lambdas[0, 0] #remove redundant matrix dimension
    lambda2 = lambdas[0, 1] #remove redundant matrix dimension
    lambda3 = lambdas[0, 2] #remove redundant matrix dimension
    lambda4 = 1 - lambda1 - lambda2 - lambda3

    return lambda1, lambda2, lambda3, lambda4

def interpolate(p, a, b, c, d):
    #print(f'interpolate args = {p}, {a}, {b}, {c}, {d}')
    if isInvalid(a) or isInvalid(b) or isInvalid(c) or isInvalid(d):
        aRGB = bRGB = cRGB = dRGB = np.array([-1.5, -1.5, -1.5])
        weightA = weightB = weightC = weightD = 1
    else:
        weightA, weightB, weightC, weightD = barycentricCoordinates(p, a, b, c, d)

        #TESTING - weight validation check
        weightSum = weightA + weightB + weightC + weightD
        #if not(weightSum >= 0.99 and weightSum <= 1.01):
            #print("ERROR: weights do not add to 1")
            #print(f'       sum={weightSum}')

        aRGB = keypointLookup(a)
        bRGB = keypointLookup(b)
        cRGB = keypointLookup(c)
        dRGB = keypointLookup(d)

    value = (aRGB * weightA) + (bRGB * weightB) + (cRGB * weightC) + (dRGB * weightD)

    #print(f'RETURNING value: {value} from interpolate()')
    return value

def getTetraVertices(p):
    #print(f'simplices: {tessellation.points[tessellation.simplices[tessellation.find_simplex(p)]]}')
    simplexIndex = tessellation.find_simplex(p)
    if simplexIndex == -1:
        return nv, nv, nv, nv

    vertices = tessellation.points[tessellation.simplices[simplexIndex]]
    #print(f'vertices = {vertices} for point p = {p}')
    a, b, c, d = vertices[0], vertices[1], vertices[2], vertices[3],

    #print(f'RETURNING VERTICES {a},{b},{c},{d} for point {p}')
    return a, b, c, d

def generate3DLUT(size, cubeSize):
    #print(f'size = {size}')
    lut = np.empty((size, size, size, 3), order='C')

    for blue in range(size):
        for green in range(size):
            for red in range(size):
                r, g, b = red*cubeSize/(size-1), green*cubeSize/(size-1), blue*cubeSize/(size-1)
                #print(f'======STARTING 3D LUT GENERATION for point: red={r}, green={g}, blue={b}======')
                p = np.array([r, g, b])
                a, b, c, d = getTetraVertices(p)

                #print(f'VERTICIES for point {p}:\n    a={a}, b={b}, c={c}, d={d}')

                lut[red, green, blue] = interpolate(p, a, b, c, d)
                #print(f'INTERPOLATION RESULTS: RGB={lut[red, green, blue]}\n\n')
    return lut

def printCubeFile(lutArray):
    print("# header")
    print(f'LUT_3D_SIZE {lutArray.shape[0]}')

    for b in lutArray:
        for g in b:
            for r in g:
                print(f'{r[0]} {r[1]} {r[2]}') #does this work?

def loadKeypointsFromCSV(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print()
                line_count += 1
            else:
                r, g, b = row[0], row[1], row[2]
                rPrime, gPrime, bPrime = row[3], row[4], row[5]
                insertKeypoint(r, g, b, rPrime, gPrime, bPrime)
                line_count += 1
        print(f'#Loaded {line_count} keypoints.')

    return

def getAllKeypointsAsNumpyArray():
    arry = np.asarray(list(keypointDict.keys()), dtype=float)
    #print(f'arry: {arry}')
    return arry

def insertKeypoint(r, g, b, x, y, z):
    keypointDict.update({ (float(r), float(g), float(b)): (float(x), float(y), float(z)) })
    return 0

def main():
    #lut dictionary --
    global keypointDict
    keypointDict = {}

    #global keypointSet
    #keypointSet = np.zeros()

    global tessellation

    #print("bla")
    loadKeypointsFromCSV('Datasets/keypointsYellow.csv')

    #list(np.asarray(keyAsTuple, dtype=np.float64)

    keypoints = getAllKeypointsAsNumpyArray()
    #print(f'keypoints: {keypoints}')
    tessellation = tessellate(keypoints)
    printCubeFile(generate3DLUT(9, 1.0))

main()
