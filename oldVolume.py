def tetrahedronVolume(a, b, c, d): #a-d are numpy arrays of form (x, y, z) representing the vertices of the tetrahedron
    sideAB = distance(a, b)
    sideAC = distance(a, c)
    sideAD = distance(a, d)
    sideBC = distance(b, c)
    sideBD = distance(b, d)
    sideCD = distance(c, d)

    print(f'sideAB = {sideAB}')
    print(f'sideAC = {sideAC}')
    print(f'sideAD = {sideAD}')
    print(f'sideBC = {sideBC}')
    print(f'sideBD = {sideBD}')
    print(f'sideCD = {sideCD}')

    X = (sideAC - sideCD + sideAD)*(sideCD + sideAD + sideAC)
    Y = (sideAB - sideBC + sideAC)*(sideBC + sideAC + sideAB)
    Z = (sideAD - sideBD + sideAB)*(sideBD + sideAB + sideAD)
    x = (sideCD - sideAD + sideAC)*(sideAD - sideAC + sideCD)
    y = (sideBC - sideAC + sideAB)*(sideAC - sideAB + sideBC)
    z =(sideBD - sideAB + sideAD)*(sideAB - sideAD + sideBD)

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

    volume = math.sqrt( (-p+q+r+s)*(p-q+r+s)*(p+q-r+s)*(p+q+r-s) )/(192*sideAB*sideAC*sideAD)
    return volume