from matrix import Cell
from functions import *


def test_matrix_constructor():
    input_values = [
        [1, 2],
        [2, 1]
    ]
    input_cells = [
        [Cell(), Cell()],
        [Cell(), Cell()]
    ]
    input_cells[0][0].value = 1
    input_cells[0][1].value = 2
    input_cells[1][0].value = 2
    input_cells[1][1].value = 1
    matrix = Matrix(input_values)
    assert matrix.cells == input_cells


def test_unsolved_matrix():
    input_values = [
        [
            1,
            1,
            1
        ],
        [
            2,
            3,
            1
        ],
        [
            1,
            3,
            2
        ]
    ]
    matrix = Matrix(input_values)
    assert not matrix.is_solved()


def test_solvable_matrix():
    input_values = [
        [
            1,
            1,
            1
        ],
        [
            2,
            3,
            1
        ],
        [
            1,
            3,
            2
        ]
    ]
    matrix = Matrix(input_values)
    assert solution_exists(matrix)[0]
    solve(matrix)
    assert not matrix.is_solved()


def test_unsolvable_matrix():
    input_values = [
        [1, 2],
        [2, 1]
    ]
    matrix = Matrix(input_values)
    assert not solution_exists(matrix)[0]
    input_values = [
        [
            1,
            1,
            1
        ],
        [
            1,
            1,
            1
        ],
        [
            1,
            1,
            1
        ]
    ]
    matrix = Matrix(input_values)
    assert not solution_exists(matrix)[0]


def test_solution_cells():
    input_values = [
        [
            1,
            1,
            1
        ],
        [
            2,
            3,
            1
        ],
        [
            1,
            3,
            2
        ]
    ]
    matrix = Matrix(input_values)
    cells = [
        [Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell()]
    ]
    cells[0][0].state = State.Colored
    cells[0][0].value = 1
    cells[0][1].state = State.NotColored
    cells[0][1].value = 1
    cells[0][2].state = State.Colored
    cells[0][2].value = 1
    cells[1][0].state = State.NotColored
    cells[1][0].value = 2
    cells[1][1].state = State.NotColored
    cells[1][1].value = 3
    cells[1][2].state = State.NotColored
    cells[1][2].value = 1
    cells[2][0].state = State.NotColored
    cells[2][0].value = 1
    cells[2][1].state = State.Colored
    cells[2][1].value = 3
    cells[2][2].state = State.NotColored
    cells[2][2].value = 2
    matrix = solve(matrix)
    assert cells == matrix.cells


def test_matrix_generation():
    assert solution_exists(Matrix(generate(3)))[0]
    assert not solution_exists(Matrix(generate(2)))[0]
