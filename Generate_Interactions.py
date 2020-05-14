import numpy as np
import sys

# Read Arbitrary XYZ file into list of coordinates
fname = sys.argv[1]
numLines = 0
with open(fname) as f:
    numLines = sum(1 for _ in f)
basis = np.genfromtxt(fname, skip_footer=numLines - 3)
basis_coords = np.genfromtxt(fname, skip_header=4, usecols=(0, 1, 2))
default_species = np.genfromtxt(fname, skip_header=4, usecols=(4))
coords = basis_coords.dot(basis)
s_distances = set()
for posA in basis_coords:
    for posB in basis_coords:
        s_distances.add(np.linalg.norm(posA - posB))
s_distances.remove(0.0)
J_dist = min(s_distances)
s_distances.remove(J_dist)
K_dist = min(s_distances)


basis_shifts = []
for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
        for k in [-1, 0, 1]:
            basis_shifts.append([i, j, k])
basis_shifts = np.array(basis_shifts)
for iA, posA in enumerate(basis_coords):  # for each element in lattice
    for iS, shift in enumerate(basis_shifts):  # shift around
        shifted_coords = basis_coords + shift
        for iB, posB in enumerate(shifted_coords):  # find the other near atoms
            distance = np.linalg.norm(posA - posB)
            if distance == J_dist:
                print(iA + 1, iB + 1, 1)
            if distance == K_dist:
                print(iA + 1, iB + 1, 2)
