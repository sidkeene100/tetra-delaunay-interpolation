import numpy as np
import scipy.spatial
import csv

filename = "keypointsKodak.csv"

global keypointDict
keypointDict = {}

with open(filename) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            #print()
            line_count += 1
        else:
            r, g, b = row[0], row[1], row[2]
            x, y, z = row[3], row[4], row[5]
            keypointDict.update({ (float(r), float(g), float(b)): (float(x), float(y), float(z)) })
            line_count += 1
    print(f'# Loaded {line_count} keypoints.')


points = np.asarray(list(keypointDict.keys()))
values = np.asarray(list(keypointDict.values()))


#keypoints
#points = np.array([(0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),(1,1,0),(1,1,1)])

#tessellate
tri = scipy.spatial.Delaunay(points)

#Generate a 3D LUT
size = 17
cubeSize=1.0
cube = np.empty((size, size, size, 6), order='F') # currently only using first 3, last 3 are there to store LUT outputs eventually
for r in range(size):
    for g in range(size):
        for b in range(size):
            cube[r, g, b, 0] = r*cubeSize/(size-1)
            cube[r, g, b, 1] = g*cubeSize/(size-1)
            cube[r, g, b, 2] = b*cubeSize/(size-1)

#points to interpolate at
targets = cube[:,:,:,:3].reshape(-1, cube[:,:,:,:3].shape[-1])

#map of tetrahedra for given points
tetrahedra = tri.find_simplex(targets)

#points of the tetrahedron(s) that contain target(s)
assignedKeyPoints = tri.points[tri.simplices[tri.find_simplex(targets)]] # is basically unused

newArray = np.copy(assignedKeyPoints)

shape = newArray.shape
for i in range(shape[0]):
    #print(f'tet: {newArray[i]}')
    for j in range(shape[1]):
        #print(f'Point : {newArray[i, j]}')
        newArray[i, j] = np.asarray( keypointDict[tuple(newArray[i, j])] )
        #print(f'Point\': {newArray[i, j]}')

#linear algebra magic
X = tri.transform[tetrahedra,:3]
Y = targets - tri.transform[tetrahedra,3]
b = np.einsum('ijk,ik->ij', X, Y)

#barycentric weights (order?) to use as coefficients
bcoords = np.c_[b, 1 - b.sum(axis=1)]

#print(f'bcoords: {bcoords}')
#print(f'akp: {assignedKeyPoints}')

output = np.flip( np.sum( (newArray * bcoords[:,:,np.newaxis]), axis=-2 ), axis=1 )
print(f'Shape: {output.shape}')

print(f'LUT_3D_SIZE {size}')
for entry in output:
    print(f'{entry[0]:.4f} {entry[1]:.4f} {entry[2]:.4f}')
#out = str(output.tolist()).replace("], [", "\n").replace(",", "").replace("[[", "").replace("]]", "")
