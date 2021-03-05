from scipy import interpolate
import sys
import csv
import numpy as np

BUFFERSIZE = 1024

def load1DKeypointsFromCSV(filename):
    '''Loads keypoints from a CSV. Format: rIn,gIn,bIn,rOut,gOut,bOut, disregards first line.'''
    luts = np.ndarray(shape=(BUFFERSIZE, 6))

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

                luts[line_count - 1, 0] = r
                luts[line_count - 1, 1] = g
                luts[line_count - 1, 2] = b
                luts[line_count - 1, 3] = rPrime
                luts[line_count - 1, 4] = gPrime
                luts[line_count - 1, 5] = bPrime

                line_count += 1
        print(f'#Loaded {line_count} keypoints.')
        return luts[:line_count-2]

def main():
    filename = sys.argv[1]
    luts = load1DKeypointsFromCSV(filename)

    redFunc = interpolate.interp1d(luts[:,0], luts[:,3], fill_value="extrapolate")
    greenFunc = interpolate.interp1d(luts[:,1], luts[:,4], fill_value="extrapolate")
    blueFunc = interpolate.interp1d(luts[:,2], luts[:,5], fill_value="extrapolate")

    for i in range(0,1024):
        print(f'RED: {i}, {redFunc(i)}')

main()
