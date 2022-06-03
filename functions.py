from copy import deepcopy
from random import shuffle, seed, randint
from time import time_ns

from matrix import NoSolutionExistsError, Matrix, State


def solve(matrix: Matrix) -> Matrix:
    t = deepcopy(matrix)
    t.finalize_unique_cells()
    if t.is_solved():
        return t
    pos = t.get_finalize_candidate_pos()
    try:
        t_copy = deepcopy(t)
        t_copy.finalize_cell(pos[0], pos[1])
        return solve(t_copy)
    except NoSolutionExistsError:
        t.color_cell(pos[0], pos[1])
        return solve(t)


def solution_exists(matrix: Matrix) -> tuple[bool, Matrix]:
    if matrix.size <= 2:
        return False, Matrix([])
    try:
        t = solve(matrix)
        for cell_column in t.cells:
            for cell in cell_column:
                if cell.state == State.Colored:
                    return True, t
    except NoSolutionExistsError:
        return False, Matrix([])


def generate(size: int) -> list[list]:
    if size == 2:
        return []
    seed(time_ns())
    data = []
    while not solution_exists(Matrix(data))[0]:
        data = []
        for i in range(0, size):
            data.append([0] * size)
        for r in range(0, size):
            for c in range(0, size):
                data[c][r] = randint(1, size)
        for i in range(0, 10):
            for r in range(0, size):
                shuffle(data[r])
            shuffle(data)
    return data
