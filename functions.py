import time
from copy import deepcopy
from random import shuffle, seed, randint
from time import time_ns
import multiprocessing as mp

from matrix import NoSolutionExistsError, Matrix, State


def solve_parallel(matrix: Matrix, deep=0):
    t = deepcopy(matrix)
    t.finalize_unique_cells()
    if t.is_solved():
        return t
    pos = t.get_finalize_candidate_pos()
    deep += 1
    if deep < 2:
        pipe1 = mp.Pipe()
        pipe2 = mp.Pipe()
        process1 = mp.Process(target=solve_by_finalize, name=f"finalize_{deep}",
                              args=(pos, t, pipe1[0], deep))
        process2 = mp.Process(target=solve_by_color, name=f"color_{deep}",
                              args=(pos, t, pipe2[0], deep))
        process1.start()
        process2.start()
        solved_by_finalize = pipe1[1].recv()
        solved_by_color = pipe2[1].recv()
        process1.join()
        process2.join()
        pipe1[1].close()
        pipe2[1].close()
        return solved_by_finalize if solved_by_finalize != "error" else solved_by_color
    else:
        solved_by_finalize = solve_by_finalize(pos, t, None, deep)
        return solved_by_finalize if solved_by_finalize != "error" else solve_by_color(pos, t, None, deep)


def solve_by_finalize(pos, t, pipe, deep):
    t_copy = deepcopy(t)
    t_copy.finalize_cell(pos[0], pos[1])
    if pipe is not None:
        pipe.send(solve_parallel(t_copy, deep))
    else:
        return solve_parallel(t_copy, deep)


def solve_by_color(pos, t, pipe, deep):
    if t.color_cell(pos[0], pos[1]) == "error":
        return "error"
    if pipe is not None:
        pipe.send(solve_parallel(t, deep))
    else:
        return solve_parallel(t, deep)


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


if __name__ == "__main__":
    test_arr = [[6, 6, 3, 2, 1, 5],
                [1, 2, 6, 3, 5, 4],
                [5, 1, 4, 2, 3, 4],
                [3, 3, 3, 5, 2, 1],
                [4, 2, 1, 6, 5, 3],
                [6, 1, 5, 4, 4, 4]]
    start = time.time()
    solve_parallel(Matrix(test_arr)).print()
    print(f"spent time: {time.time()-start}")
