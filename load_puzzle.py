
import csv
import sys
import numpy as np
from itertools import product

def load_puzzle(name):
    with open(name, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        lists = [[int(c) for c in row] for row in reader]
    return np.array(lists)


def get_quadrant_idx(i, j):
    return i // 3, j // 3

def get_quadrant(q1, q2):
    return grid[q1*3:(q1+1)*3, q2*3:(q2+1)*3]

def get_quadrant_cell(i, j):
    q1, q2 = get_quadrant_idx(i, j)
    return get_quadrant(q1, q2)

def quadrants_with(vector, i):
    found = np.array([i in [j for k in vector[idx:idx+3] for j in k] for idx in [0, 3, 6]])
    return np.arange(3)[found]


def quadrant_iterator(q1, q2):
    return [[q1+i, q2+j] for j in range(3) for i in range(3)]



def possible_values(grid, i, j):
    """ Return all possible values of a cell """
    if grid[i, j] != 0:
        return []
    # q1, q2 = get_quadrant_idx(i, j)
    # quadrant_vals = grid[q1*3:(q1+1)*3, q2*3:(q2+1)*3]
    quadrant_vals = get_quadrant_cell(i, j)

    vals = list(grid[i, :])
    vals.extend(list(grid[:, j]))
    vals.extend(list(quadrant_vals.flatten()))
    # vals = list(set(vals))
    return [i for i in range(10) if i not in vals]



def narrow_values(grid, values):
    """ Discard some 'possible_values' """

    for i in range(9):
        start = i * 9
        vector_values = [values[i] for i in range(start, start+9)]
        # vector_values = list(set([j for i in vector_values for j in i]))
        for n in range(1, 10):
            qds = quadrants_with(vector_values, n)
            if len(qds) == 1:
                pass
                
                
        



def all2():
    return product(range(9), repeat=2)

def printg(grid, i):
    print("Iteration %u:" % i)
    print(grid)

def solve_sudoku(grid):
    """ Solves a puzzle """
    combs = product(range(9), repeat=2)
    i = 0
    printg(grid, i)
    while 0 in grid:
        alive = False
        values = [possible_values(grid, i, j) for i, j in all2()]
        for vals, idx in zip(values, all2()):
            if len(vals) == 1:
                alive = True
                grid[idx[0], idx[1]] = vals[0]

        if not alive:
            print("I could not find a solution :(")
            sys.exit(0)
        i += 1
        printg(grid, i)


if __name__ == "__main__":
    grid = load_puzzle('puzz1.csv')
    print(grid)
    solve_sudoku(grid)

