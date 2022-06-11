from fastapi import FastAPI, status, HTTPException, Body
from functions import *
from matrix import Cell

tags_metadata = [
    {
        "name": "test",
        "description": "Endpoint to test how the program solves the puzzle"
    },
    {
        "name": "solve",
        "description": "Endpoint to solve the puzzle according to the input"
    },
    {
        "name": "generate",
        "description": "Endpoint to generate input for the puzzle"
    }
]

example_ints = Body(default=None, example=[
    [0]
])

example_cells = Body(default=None, example=[
    [Cell()]
])

app = FastAPI(
    title="Puzzle Solver and Generator",
    description="Application to solve the puzzle or generate its conditions"
)


@app.get("/test", tags=["test"], name="Tester", response_model=list[list[Cell]], responses={
    200: {
        "content": {
            "application/json": {
                example_cells
            }
        }
    }
})
async def test() -> list[list[Cell]]:
    test_arr = [[6, 6, 3, 2, 1, 5],
                [1, 2, 6, 3, 5, 4],
                [5, 1, 4, 2, 3, 4],
                [3, 3, 3, 5, 2, 1],
                [4, 2, 1, 6, 5, 3],
                [6, 1, 5, 4, 4, 4]]
    return solve_parallel(Matrix(test_arr)).cells


@app.post("/solve", tags=["solve"], name="Solver", response_model=list[list[Cell]], responses={
    200: {
        "content": {
            "application/json": {
                example_cells
            }
        }
    },
    400: {
        "model": str,
        "description": "No solution exists for the input data"
    }
})
async def solve_puzzle(matrix_list: list[list[int]]) -> list[list[Cell]]:
    matrix = Matrix(matrix_list)
    solution = solution_exists(matrix)
    if not solution_exists(matrix)[0]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No solution exists for the input data")
    return solution[1].cells


@app.get("/generate", tags=["generate"], name="Generator", response_model=list[list[int]], responses={
    200: {
        "content": {
            "application/json": {
                "example": example_ints
            }
        }
    },
    400: {
        "model": str,
        "description": "No input exists for the solution data"
    }
})
async def generate_puzzle(size: int = 5) -> list[list[int]]:
    if size <= 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No input exists for the solution data")
    return generate(size)
