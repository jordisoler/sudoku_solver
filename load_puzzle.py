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

    def __hash__(self):
        return hash(self.n)

    def remove(self, value):
        try:
            self.values.remove(value)
        except ValueError:
            pass

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
        valid_elements = tuple(i for i in range(10))
        all_valid = all(tuple(i.n in valid_elements for i in self))
        my_elements = [c.n for c in self if c.n != 0]
        return len(set(my_elements)) == len(my_elements) and all_valid

    def remove(self, value, rang):
        has_changed = False
        for c, actual_rang, idx in zip(self, np.repeat([0, 1, 2], 3), range(9)):
            if actual_rang != rang:
                values_before = [x for x in c.values]
                c.remove(value)
                if values_before != c.values:
                    has_changed = True
        return has_changed

    def get_subsets(self, cells, n):
        groups = [0, 1, 2]
        groups_with_n = set()
        for gr in groups:
            for c in cells[gr*3:(gr+1)*3]:
                if n in c:
                    groups_with_n.add(gr)
        return tuple(groups_with_n)


class linset(cellset):
    def whichsubset(self, n):
        return self.get_subsets(self.cells, n)


class boxset(cellset):
    def whichsubset_v(self, n):
        return self.get_subsets(self.cells.T.flatten(), n)

    def whichsubset_h(self, n):
        return self.get_subsets(self.cells.flatten(), n)

    def remove(self, value, rang, axis):
        has_changed = False
        def itervalues():
            base = self.cells.T.flatten() if axis == 0 else self.cells.flatten()
            for c in base:
                yield c
        for c, actual_rang, idx in zip(itervalues(), np.repeat([0, 1, 2], 3), range(9)):
            if actual_rang != rang:
                v_before = [i for i in c.values]
                c.remove(value)
                v_after = [i for i in c.values]
                if v_before != v_after:
                    has_changed = True
        return has_changed


class Sudoku:

    def __init__(self):
        self.grid = np.zeros((9, 9))
        self.update_possibles = True

    def __iter__(self):
        for i in range(9):
            for j in range(9):
                yield self.grid[i, j], (i, j)

    def __str__(self, verbosity=0):

        def show(num):
            return '_' if num == 0 else str(num)
        hline = ' ' + '|' + '-'*23 + '|\n'
        out = ''
        for row, idx in zip(self.grid, range(9)):
            if idx % 3 == 0:
                out += hline
                # out += ' ' + '-'*25 + '\n'
            for i in range(9):
                if i % 3 == 0:
                    out += ' |'
                out += ' ' + show(row[i].n)
            out += ' |'
            # out += ' '.join([str(el.n) for el in row])
            out += '\n'
        if verbosity >= 1:
            for c, idx in self:
                out += str((idx, c.n, c.values)) + '\n'
        return out + hline

    def is_valid(self):
        for box, idx in self.iterboxes():
            if not box.is_valid():
                print('Not valid box',idx)
                print([c.n for c in box])
                return False
        for hlin, idx in self.iterh():
            if not hlin.is_valid():
                print('Not valid hlin',idx)
                return False
        for vlin, idx in self.iterv():
            if not vlin.is_valid():
                print('Not valid vlin',idx)
                return False
        return True

    def num_known(self):
        return len([1 for c, _ in self if c.n != 0])

    def iterboxes(self):
        for i in range(3):
            for j in range(3):
                i_b, j_b = i*3, j*3
                yield boxset(self.grid[i_b:i_b+3, j_b:j_b+3]), (i_b, j_b)

    def iterh(self):
        for i in range(9):
            yield linset(self.grid[i, :]), i

    def iterv(self):
        for i in range(9):
            yield linset(self.grid[:, i]), i

    def box_from_idx(self, i, j):
        i_b, j_b = (i // 3) * 3, (j // 3) * 3
        return boxset(self.grid[i_b:i_b+3, j_b:j_b+3])

    def reduce_possibilities(self):

        has_changed = False

        for box, idx in self.iterboxes():
            for n in range(1, 10):
                subs = box.whichsubset_h(n)
                if len(subs) == 1:
                    cset = linset(self.grid[idx[0]+subs[0], :])
                    has_changed = has_changed or cset.remove(n, idx[1]/3)

                subs = box.whichsubset_v(n)
                if len(subs) == 1:
                    cset = linset(self.grid[:, idx[1]+subs[0]])
                    has_changed = has_changed or cset.remove(n, idx[0]/3)

        for hset, i in self.iterh():
            for n in range(1, 10):
                subs = hset.whichsubset(n)
                if len(subs) == 1:
                    cset = self.box_from_idx(i, subs[0]*3)
                    has_changed = has_changed or cset.remove(n, i%3, 1)

        for vset, j in self.iterv():
            for n in range(1, 10):
                subs = vset.whichsubset(n)
                if len(subs) == 1:
                    cset = self.box_from_idx(subs[0]*3, j)
                    has_changed = has_changed or cset.remove(n, j%3, 0)
        return has_changed

    def is_done(self):
        return int(0) not in [c for c, _ in self]

    def subsets_cell(self, i, j):
        min_i = (i // 3) * 3
        min_j = (j // 3) * 3

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
        if self.grid[i, j].n != 0:
            return []
        subsets = self.subsets_cell(i, j)
        values_now = set()
        for subset in subsets:
            for element in subset:
                values_now.add(element.n)
        return [val for val in range(1, 10) if val not in values_now]

    def get_first_possible_values(self, i, j):
        self.grid[i, j].values = self.possible_values(i, j)

    def certain_cells(self):
        return (c for c, _ in self if c.values is not None and len(c.values) == 1)

    def solve(self):

        alive = True
        it = 0
        while alive and not self.is_done():
            print("Iteration {}".format(it))
            print("num_known {}".format(self.num_known()))
            print(self)

            if not self.is_valid():
                print('Sorry, I was wrong')
                print(self)
                sys.exit(1)

            if self.update_possibles:
                def init_cell(idx):
                    self.get_first_possible_values(idx[0], idx[1])
                for _, idx in self:
                    init_cell(idx)
                self.update_possibles = False
            else:
                has_changed = self.reduce_possibilities()
                if not has_changed:
                    alive = False

            certains = self.certain_cells()
            for c in self.certain_cells():
                c.assign()
                self.update_possibles = True
            it += 1

        if alive:
            print("The sudoku has been solved! :)")
        else:
            print("I could not find a solution :(")


if __name__ == "__main__":
    sudoku = Sudoku()
    sudoku.load('puzz1.csv')
    sudoku.solve()
    print(sudoku)

