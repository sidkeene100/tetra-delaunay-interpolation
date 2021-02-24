import numpy as np
from scipy.spatial import Delaunay
import math
import csv

#TODO:
# optimization - height and volume only really use the distances between vertices.
# Since we have to calculate all distances for a given p when locating the 4 nearest keypoints,
# we should re-use thse distances rather than re-calculating them

def distance(a, b): #a, b are numpy arrays of (x, y, z)
    return np.linalg.norm(a-b)

def tetrahedronVolume(a, b, c, d): #a-d are numpy arrays of form (x, y, z) representing the vertices of the tetrahedron
    print("\nFUNCTION CALL: tetrahedronVolume() --")
    #Function thows error if tetrahedron is degenerate (all 4 vertices are coplanar)
    # print(f'a = {a}')
    # print(f'b = {b}')
    # print(f'c = {c}')
    # print(f'd = {d}')

    u = distance(a, b)
    v = distance(a, c)
    w = distance(a, d)
    W = distance(b, c)
    V = distance(b, d)
    U = distance(c, d)

    print(f'u = {u}')
    # print(f'v = {v}')
    print(f'w = {w}')
    # print(f'W = {W}')
    print(f'V = {V}')
    # print(f'U = {U}')

    X = (w-U+v)*(U+v+w)
    x = (U-v+w)*(v-w+U)
    Y = (u-V+w)*(V+w+u)
    y = (V-w+u)*(w-u+V)
    Z = (v-W+u)*(W+u+v)
    z = (W-u+v)*(u-v+W)

    print(f'X = {X}')
    print(f'Y = {Y}')
    print(f'Z = {Z}')
    print(f'x = {x}')
    print(f'y = {y}')
    print(f'z = {z}')

    p = math.sqrt(x*Y*Z)
    q = math.sqrt(y*Z*X)
    r = math.sqrt(z*X*Y)
    s = math.sqrt(x*y*z)

    # print(f'p = {p}')
    # print(f'q = {q}')
    # print(f'r = {r}')
    # print(f's = {s}')

    volume = math.sqrt( (-p+q+r+s)*(p-q+r+s)*(p+q-r+s)*(p+q+r-s) )/(192*u*v*w)
    if math.isnan(volume):
        return 0
    return volume

def tetrahedronHeight(a, b, c, d): #the height of a above the plane bcd
    sideBC = distance(b, c)
    sideBD = distance(b, d)
    sideCD = distance(c, d)

    p = (sideBC + sideBD + sideCD)/2
    area = math.sqrt( p*(p-sideBC)*(p-sideBD)*(p-sideCD) )

    volume = tetrahedronVolume(a, b, c, d)
    height = 3 * volume / area
    # print(f'height {height} = 3 * {volume}[volume] over {area}[area]')
    return height

def tessellate(points): #tessellate an array of points, shape: np.array([[0, 0, 0], [0, 1.1, 0], [1, 0, 0], [1, 1, 0]])
    return Delaunay(points)

def keypointLookup(rgb): #rgb is numpy array #same as keypointFunction()
    return np.asarray(keypointDict[rgb[0], rgb[1], rgb[2]])

def interpolate(p, a, b, c, d):
    print(f'plane_distance: {tessellation.plane_distance(p)}')

    heightA = tetrahedronHeight(a, b, c, d)
    heightB = tetrahedronHeight(b, a, c, d)
    heightC = tetrahedronHeight(c, b, a, d)
    heightD = tetrahedronHeight(d, b, c, a)

    heightP_a = tetrahedronHeight(p, b, c, d)
    heightP_b = tetrahedronHeight(p, a, c, d)
    heightP_c = tetrahedronHeight(p, b, a, d)
    heightP_d = tetrahedronHeight(p, b, c, a)

    weightA = (heightP_a / heightA)
    weightB = (heightP_b / heightB)
    weightC = (heightP_c / heightC)
    weightD = (heightP_d / heightD)

    print(f'Weight A = {weightA} = {heightP_a} over {heightA}')
    print(f'Weight B = {weightB} = {heightP_b} over {heightB}')
    print(f'Weight C = {weightC} = {heightP_c} over {heightC}')
    print(f'Weight D = {weightD} = {heightP_d} over {heightD}')
    print(f'sum = {weightA + weightB + weightC + weightD}')
    #TESTING - weight validation check
    if weightA + weightB + weightC + weightD != 1:
        print("ERROR: weights do not add to 1")

    aRGB = keypointLookup(a)
    bRGB = keypointLookup(b)
    cRGB = keypointLookup(c)
    dRGB = keypointLookup(d)

    value = (aRGB * weightA) + (bRGB * weightB) + (cRGB * weightC) + (dRGB * weightD)

    print(f'RETURNING value: {value} from interpolate()')
    return value

def new_interpolate(p, a, b, c, d):
    return 0

def getTetraVertices(p):
    #print(f'simplices: {tessellation.points[tessellation.simplices[tessellation.find_simplex(p)]]}')
    vertices = tessellation.points[tessellation.simplices[tessellation.find_simplex(p)]]
    print(f'vertices = {vertices} for point p = {p}')
    a, b, c, d = vertices[0], vertices[1], vertices[2], vertices[3],

    print(f'RETURNING VERTICES {a},{b},{c},{d} for point {p}')
    return a, b, c, d

def generate3DLUT(size, cubeSize):
    #print(f'size = {size}')
    lut = np.empty((size, size, size, 3), order='F')

    for red in range(size):
        for green in range(size):
            for blue in range(size):
                r, g, b = red*cubeSize/size, green*cubeSize/size, blue*cubeSize/size
                print(f'======STARTING 3D LUT GENERATION for point: red={r}, green={g}, blue={b}======')
                p = np.array([r, g, b])
                a, b, c, d = getTetraVertices(p)

                print(f'VERTICIES for point {p}:\n    a={a}, b={b}, c={c}, d={d}')

                lut[red, green, blue] = interpolate(p, a, b, c, d)
                print(f'INTERPOLATION RESULTS: RGB={lut[red, green, blue]}\n\n')
    return lut

def printCubeFile(lutArray):
    print("# header")
    print(f'LUT_3D_SIZE {lutArray.shape[0]}')

    for r in lutArray:
        for g in r:
            for b in g:
                print(f'owo {b}') #does this work?

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
        print(f'Loaded {line_count} keypoints.')

    return

def getAllKeypointsAsNumpyArray():
    arry = np.asarray(list(keypointDict.keys()), dtype=float)
    print(f'arry: {arry}')
    return arry

def insertKeypoint(r, g, b, x, y, z):
    keypointDict.update({ (float(r), float(g), float(b)): (float(x), float(y), float(z)) })
    return 0

def keypointFunction(rgb):
    return np.asarray(keypointDict[rgb[0], rgb[1], rgb[2]])

def main():
    #lut dictionary --
    global keypointDict
    keypointDict = {}

    #global keypointSet
    #keypointSet = np.zeros()

    global tessellation

    print("bla")
    loadKeypointsFromCSV('keypoints.csv')

    #list(np.asarray(keyAsTuple, dtype=np.float64)

    keypoints = getAllKeypointsAsNumpyArray()
    print(f'keypoints: {keypoints}')
    tessellation = tessellate(keypoints)
    printCubeFile(generate3DLUT(9, 1.0))

main()
