from enum import Enum

from pydantic import BaseModel


class State(str, Enum):
    Unknown = "Unknown"
    NotColored = "Not colored"
    Colored = "Colored"


class Cell(BaseModel):
    value: int = 0
    state: State = State.Unknown

    def __eq__(self, other):
        return self.value == other.value and self.state == other.state


class NoSolutionExistsError(ValueError):
    pass


class DisjointSets:
    def __init__(self, size):
        self.parents = [-1] * size

    def assert_element_range(self, e):
        if e < 0 or e >= len(self.parents):
            raise ValueError("Element index is out of range")

    def find_set(self, e):
        self.assert_element_range(e)
        root = e
        while self.parents[root] >= 0:
            root = self.parents[root]
        while self.parents[e] >= 0:
            parent = self.parents[e]
            self.parents[e] = root
            e = parent
        return root

    def link_sets(self, set1, set2):
        self.assert_element_range(set1)
        self.assert_element_range(set2)
        if self.parents[set1] >= 0 or self.parents[set2] >= 0:
            raise ValueError("At least one element is not root")
        if set1 != set2:
            rank1 = -self.parents[set1] - 1
            rank2 = -self.parents[set2] - 1
            if rank1 < rank2:
                self.parents[set1] = set2
            elif rank2 < rank1:
                self.parents[set2] = set1
            else:
                self.parents[set1] = set2
                self.parents[set2] -= 1

    def union_sets(self, e1, e2):
        root1 = self.find_set(e1)
        root2 = self.find_set(e2)
        self.link_sets(root1, root2)


class Matrix:
    def __init__(self, init_values):
        self.size = len(init_values)
        self.row_counts = []
        for i in range(0, self.size):
            self.row_counts.append([0] * (self.size + 1))
        self.column_counts = []
        for i in range(0, self.size):
            self.column_counts.append([0] * (self.size + 1))
        self.unknown_cell_count = self.size ** 2
        self.deleted_trees = DisjointSets(self.size ** 2 + 1)
        self.cells = []
        act_row = 0
        for row in init_values:
            act_column = 0
            row_cells = []
            for value in row:
                cell = Cell()
                cell.value = value
                cell.state = State.Unknown
                row_cells.append(cell)
                self.row_counts[act_row][value] += 1
                self.column_counts[act_column][value] += 1
                act_column += 1
            self.cells.append(row_cells)
            act_row += 1

    def is_solved(self):
        return self.unknown_cell_count == 0

    def finalize_unique_cells(self):
        for r in range(0, self.size):
            for c in range(0, self.size):
                cell = self.cells[r][c]
                if cell.state != State.Unknown:
                    continue
                value = cell.value
                if self.row_counts[r][value] == 1 and self.column_counts[c][value] == 1:
                    cell.state = State.NotColored
                    self.row_counts[r][value] = 0
                    self.column_counts[c][value] = 0
                    self.unknown_cell_count -= 1

    def color_cell(self, row, column):
        cell = self.cells[row][column]
        if cell.state != State.Unknown:
            raise ValueError("Tried to set an entry's state multiple times")
        r_offs = 0
        c_offs = -1
        for i in range(0, 4):
            r = row + r_offs
            c = column + c_offs
            if 0 <= r < self.size and 0 <= c < self.size and self.cells[r][c].state == State.Colored:
                raise NoSolutionExistsError("Colored neighbor found")
            r_offs, c_offs = -c_offs, r_offs
        cell_set = row * self.size + column + 1
        if row == 0 or row == self.size - 1 or column == 0 or column == self.size - 1:
            self.deleted_trees.union_sets(0, cell_set)
        r_offs = -1
        c_offs = -1
        for i in range(0, 4):
            r = row + r_offs
            c = column + c_offs
            diagonal_neighbor_set = r * self.size + c + 1
            if 0 <= r < self.size and 0 <= c < self.size and self.cells[r][c].state == State.Colored:
                diagonal_root = self.deleted_trees.find_set(diagonal_neighbor_set)
                cell_root = self.deleted_trees.find_set(cell_set)
                if diagonal_root != cell_root:
                    self.deleted_trees.link_sets(diagonal_root, cell_root)
                else:
                    raise NoSolutionExistsError("Circular neighbors found")
            r_offs, c_offs = -c_offs, r_offs
        cell.state = State.Colored
        value = cell.value
        self.row_counts[row][value] -= 1
        self.column_counts[column][value] -= 1
        self.unknown_cell_count -= 1
        r_offs = 0
        c_offs = 1
        for i in range(0, 4):
            r = row + r_offs
            c = column + c_offs
            if 0 <= r < self.size and 0 <= c < self.size and cell.state == State.Unknown:
                self.finalize_cell(r, c)
            r_offs, c_offs = - c_offs, r_offs

    def finalize_cell(self, row, column):
        cell = self.cells[row][column]
        if cell.state != State.Unknown:
            raise ValueError("Tried to set an entry's state multiple times")
        cell.state = State.NotColored
        value = cell.value
        self.row_counts[row][value] -= 1
        self.column_counts[column][value] -= 1
        self.unknown_cell_count -= 1
        if self.column_counts[column][value] > 0:
            for r in range(0, self.size):
                cell = self.cells[r][column]
                if r != row and cell.value == value and cell.state == State.Unknown:
                    self.color_cell(r, column)
        if self.row_counts[row][value] > 0:
            for c in range(0, self.size):
                cell = self.cells[row][c]
                if c != column and cell.value == value and cell.state == State.Unknown:
                    self.color_cell(row, c)

    def get_finalize_candidate_pos(self):
        r_max = 0
        c_max = 0
        max_count = 0
        for r in range(0, self.size):
            for c in range(0, self.size):
                for v in range(1, self.size + 1):
                    cell = self.cells[r][c]
                    if cell.state != State.Unknown:
                        continue
                    act_count = self.row_counts[r][v] + self.column_counts[c][v] - 1
                    if act_count > max_count:
                        max_count = act_count
                        r_max = r
                        c_max = c
        return r_max, c_max
