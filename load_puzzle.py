import csv
import sys
import numpy as np
from itertools import product


class cell:

    def __init__(self, n):
        self.n = n
        self.values = None

    def __iter__(self):
        for v in self.values:
            yield v

    def __eq__(self, lhs):
        return lhs == self.n

    def __str__(self):
        return(str(self.n))

    def assign(self):
        if len(self.values) != 1:
            print("Cell assign error")
            sys.exit(1)
        self.n = self.values.pop()

class cellset:

    def __init__(self, cells):
        self.cells = cells

    def __iter__(self):
        for c in self.cells.flatten():
            yield c

    def is_valid(self):
        siz = len(self)
        valid_elements = tuple(i for i in range(10))
        all_valid = all(tuple(i.n in valid_elements for i in self.cells))
        return siz == 9 and len(set(self.cells)) == siz and all_valid

    def get_subsets(self, n):
        groups = [0, 1, 2]
        groups_with_n = []
        for gr in groups:
            if n in self.cells[gr*3:(gr+1)*3]:
                groups_with_n.append(gr)
        return groups_with_n


class linset(cellset):
    def whichsubset(self, n):
        return self.get_subsets(n)


class boxset(cellset):
    def whichsubset_v(self, n):
        return self.get_subsets(self.cells.flatten())

    def whichsubset_h(self, n):
        return self.get_subsets(self.cells.T.flatten())


class Sudoku:

    def __init__(self):
        self.grid = np.zeros((9, 9))

    def __iter__(self):
        for i in range(9):
            for j in range(9):
                yield self.grid[i, j], (i, j)

    def __str__(self):
        h_line = '|' + '-'*17 + '|\n'
        out = ''
        for i in range(9):
            if i % 3 == 0:
                out += h_line
            nums = [str(c.n) for c in self.grid[i, :]]
            subrows = [' '.join(nums[idx:idx+3]) for idx in (1, 2, 3)]
            out += '|' + '|'.join(subrows) + '|\n'
        return out + h_line

    def is_done(self):
        return int(0) not in [c for c, _ in self]

    def subsets_cell(self, i, j):
        min_i = i // 3
        min_j = j // 3

        box = boxset(self.grid[min_i:min_i+3, min_j:min_j+3])
        hor = linset(self.grid[i, :])
        ver = linset(self.grid[:, j])
        return hor, ver, box

    def load(self, name):
        with open(name, 'r') as f:
            reader = csv.reader(f, delimiter=';')
            lists = [[cell(int(c)) for c in row] for row in reader]
        self.grid = np.array(lists)

    def possible_values(self, i, j):
        subsets = self.subsets_cell(i, j)
        values_now = set()
        map(values_now.add, (element for subset in subsets for
                             element in subset))
        return [val for val in range(1, 10) if i not in values_now]

    def get_first_possible_values(self, i, j):
        self.grid[i, j].values = self.possible_values(i, j)

    def certain_cells(self):
        return (c for c, _ in self if c.values is not None and len(c.values) == 1)

    def solve(self):

        alive = True
        it = 0
        while alive and not self.is_done():
            print("Iteration {}".format(it))
            print(self)
            print()

            alive = False

            def init_cell(idx):
                self.get_first_possible_values(idx[0], idx[1])
            map(init_cell, (idx for _, idx in self))

            certains = self.certain_cells()
            for c in self.certain_cells():
                print('found')
                c.assign()
                alive = True
            it += 1
        if alive:
            print("The sudoku has been solved! :)")
        else:
            print("I could not find a solution :(")


if __name__ == "__main__":
    sudoku = Sudoku()
    sudoku.load('puzz1.csv')
    sudoku.solve()

