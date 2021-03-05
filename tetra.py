import numpy as np
from scipy.spatial import Delaunay
import math
import csv

#GLOBAL DEFINITIONS:
nv = np.array([-1.0, -1.0, -1.0]) #value to use for out-of-gamut points

#TODO: proper gamut mapping
#TODO: Remove hard coded args, get args from CLI

def isInvalid(point):
    '''Given a point (type np.array, size 3), determines if the point is valid or out-of-gamut.'''
    if point[0] == nv[0] or point[1] == nv[1] or point[2] == nv[2]:
        return True
    return False

def tessellate(points):
    '''Returns Delaunay tesselation an array of points, input shape: np.array([[0, 0, 0], ..., [1, 1, 0]])'''
    return Delaunay(points)

def keypointLookup(rgb):
    '''Given an input RGB triplet, returns its output triplet'''
    return np.asarray(keypointDict[rgb[0], rgb[1], rgb[2]])

def barycentricCoordinates(r, r1, r2, r3, r4):
    '''Given a point r inside the tetrahedron formed by r1-r4, calculates r's Barycentric Coordinates'''
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
    '''p is a point inside the tetrahedron formed by points a-d. Performs a Barycentric interpolation.'''
    if isInvalid(a) or isInvalid(b) or isInvalid(c) or isInvalid(d): #TODO: add more complex out-of-gamut handling
        aRGB = bRGB = cRGB = dRGB = nv
        weightA = weightB = weightC = weightD = 1
    else:
        weightA, weightB, weightC, weightD = barycentricCoordinates(p, a, b, c, d)

        aRGB = keypointLookup(a)
        bRGB = keypointLookup(b)
        cRGB = keypointLookup(c)
        dRGB = keypointLookup(d)

    value = (aRGB * weightA) + (bRGB * weightB) + (cRGB * weightC) + (dRGB * weightD)

    return value

def getTetraVertices(p):
    '''Given point p, returns points a,b,c,d forming the tetrahedron encompassing p.'''
    simplexIndex = tessellation.find_simplex(p)
    if simplexIndex == -1:
        return nv, nv, nv, nv

    vertices = tessellation.points[tessellation.simplices[simplexIndex]]
    a, b, c, d = vertices[0], vertices[1], vertices[2], vertices[3],

    return a, b, c, d

def generate3DLUT(size, cubeSize):
    '''Generates a 3D LUT with size samples per channel, and cubeSize as the domain (usually 1.0)'''
    lut = np.empty((size, size, size, 3), order='C')

    for blue in range(size):
        for green in range(size):
            for red in range(size):
                r, g, b = red*cubeSize/(size-1), green*cubeSize/(size-1), blue*cubeSize/(size-1)
                p = np.array([r, g, b])
                a, b, c, d = getTetraVertices(p)

                lut[red, green, blue] = interpolate(p, a, b, c, d)
    return lut

def printCubeFile(lutArray):
    '''Prints a given 3D LUT in .cube format.'''
    print("# header")
    print(f'LUT_3D_SIZE {lutArray.shape[0]}')

    for slice in lutArray:
        for line in slice:
            for point in line:
                print(f'{point[2]} {point[1]} {point[0]}') #SWAPPED ¯\_(ツ)_/¯

def loadKeypointsFromCSV(filename):
    '''Loads keypoints from a CSV. Format: rIn,gIn,bIn,rOut,gOut,bOut, disregards first line.'''
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
    '''Extracts keypoint input positions from the global input-output dict.'''
    arry = np.asarray(list(keypointDict.keys()), dtype=float)
    return arry

def insertKeypoint(r, g, b, x, y, z):
    '''Adds a keypoint input-output to the global dict.'''
    keypointDict.update({ (float(r), float(g), float(b)): (float(x), float(y), float(z)) })
    return 0

def main():
    global keypointDict
    keypointDict = {}

    global tessellation

    loadKeypointsFromCSV('Datasets/keypointsKodak.csv')

    keypoints = getAllKeypointsAsNumpyArray()
    tessellation = tessellate(keypoints)
    printCubeFile(generate3DLUT(9, 1.0))

main()
