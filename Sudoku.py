import copy
import numpy as np

def is_valid_value(board: np.ndarray, position: tuple, value: int) -> (bool, list):
    """
    Check if a value can be placed to a specific position on the board.
    :param board: the board to be checked
    :param position: the position to place the new value
    :param value: the value to put in
    :return: (True, []) if the value can be placed at this position (no same value in the same column,
                        row and 3x3 square).
             (False, conflicting positions) otherwise
    """
    row, col = position
    conflicts = []
    conflicts += [(row, c) for c in range(board.shape[0]) if board[row, c] == value and (row, c) not in conflicts]
    conflicts += [(r, col) for r in range(board.shape[1]) if board[r, col] == value and (r, col) not in conflicts]
    start_row = row - row % 3
    start_col = col - col % 3
    conflicts += [(r, c) for r in range(start_row, start_row + 3)
                  for c in range(start_col, start_col + 3) if board[r, c] == value and (r, c) not in conflicts]
    return len(conflicts) == 0, conflicts

def sorted_values(domains: dict, unassigned: np.ndarray, position: tuple) -> list:
    """
    Sort the values list according to the least affected value
    :param domains: The current domains of each positions on the board
    :param unassigned: The unassigned positions on the board
    :param position: The position where the values list should be sorted
    :return: A sorted list of the least affected values
    """
    values = domains[position]
    unassigned = [tuple(pos) for pos in unassigned]
    affected = {value: 0 for value in values}
    for value in values:
        for u in unassigned:
            if value in domains[u]:
                affected[value] += 1
    sorted_list = sorted(affected.keys(), key=lambda v: affected[v])
    return sorted_list


def solve(board: np.ndarray, domains: dict = None) -> (np.ndarray, bool):
    """
    Solve the sudoku board using backtracking and forward checking.
    :param board: The board to be solved.
    :param domains: A dictionary contains the domain of all unassigned position. It is used for forward checking.
    :return: The solved board and True if the board is solvable.
             None and False if the board is not solvable.
    """
    if not 0 in board:
        return board, True
    if domains is None:
        domains = get_domains(board)
    unassigned = np.argwhere(board == 0)
    unassigned_sorted = sorted([tuple(pos) for pos in unassigned], key=lambda pos: len(domains[pos]))
    for position in unassigned_sorted:
        position = tuple(position)
        values = sorted_values(domains, unassigned, position)
        for value in values:
            valid, _ = is_valid_value(board, position, value)
            if not valid:
                continue
            board[position] = value
            new_domains = forward_checking(domains, unassigned, position, value)
            if any(len(new_domains[tuple(d)]) == 0 for d in unassigned):
                continue
            solved_board, solved = solve(board, new_domains)
            if solved:
                return solved_board, True
            board[position] = 0
        return None, False
    return None, False


def forward_checking(domains: dict, unassigned: np.ndarray, position: tuple, value: int) -> dict:
    """
    Remove the value assigned into one position from the domain of all unassigned neighbour positions.
    :param domains: The current domain of the neighbours
    :param unassigned: The unassigned positions on board
    :param position: The position where a new value is assigned
    :param value: The value to assign into the position
    :return: The new domains after removing
    """
    domains = copy.deepcopy(domains)
    domains = remove_value(domains, value, np.unique(np.concatenate((get_horizontal(position, unassigned),
                                                                     get_vertical(position, unassigned),
                                                                     get_box(position, unassigned))), axis=0))
    return domains


def get_domains(board: np.ndarray) -> dict:
    """
    Get the domain of all unassigned position on a sudoku board
    :param board: The board to get the domains from
    :return: A dictionary where the keys are the positions and the values are the domains
    """
    unassigned = [tuple(pos) for pos in np.argwhere(board == 0)]
    domains = {}
    for pos in unassigned:
        domains.update({pos: [v for v in range(1, 10)]})
    return domains


def remove_value(domains: dict, value: int, region: np.ndarray) -> dict:
    """
    Remove a specific value from the domains of neighbouring positions
    :param value: The value to be removed
    :param domains: The current domains of the board
    :param region: The positions where the value should be removed from
    :return: The new domains after removing
    """
    for r in region:
        r = tuple(r)
        if r in domains:
            domains[r] = [v for v in domains[r] if v != value]
    return domains


def get_horizontal(position: tuple, unassigned: np.ndarray) -> np.ndarray:
    """
    Get all the unassigned neighbouring position in the horizontal direction.
    :param position: The position where the neighbours should be found.
    :param unassigned: All the  positions that are unassigned
    :return: The unassigned position in horizontal direction
    """
    mask = unassigned[:, 0] == position[0]
    return unassigned[mask]


def get_vertical(position: tuple, unassigned: np.ndarray) -> np.ndarray:
    """
    Get all the unassigned neighbouring position in the vertical direction.
    :param position: The position where the neighbours should be found.
    :param unassigned: All the  positions that are unassigned
    :return: The unassigned position in vertical direction
    """
    mask = unassigned[:, 1] == position[1]
    return unassigned[mask]


def get_box(position: tuple, unassigned: np.ndarray) -> np.ndarray:
    """
    Get all the unassigned neighbouring position in the 3x3 square.
    :param position: The position where the neighbours should be found.
    :param unassigned: All the  positions that are unassigned
    :return: The unassigned position in a 3x3 square
    """
    start_row = position[0] - position[0] % 3
    start_column = position[1] - position[1] % 3
    mask = ((start_row <= unassigned[:, 0]) & (unassigned[:, 0] < start_row + 3)) & \
           ((start_column <= unassigned[:, 1]) & (unassigned[:, 1] < start_column + 3))
    return unassigned[mask]


def generate(board: np.ndarray, size: int, num: int) -> (np.ndarray, np.ndarray):
    """
    Generate a new sudoku board with the given size and a given number of unassigned position
    by shuffling from a fully solved sudoku board
    :param board: The pre-solved sudoku board
    :param size: The size of the sudoku board
    :param num: The number of unassigned position
    :return:
    """
    for _ in range(10):
        if np.random.rand() > 0.5:
            box = np.random.choice(3)
            r1, r2 = np.random.choice(range(box * 3, (box + 1) * 3), size=2)
            board[[r1, r2], :] = board[[r2, r1], :]
        if np.random.rand() > 0.5:
            box = np.random.choice(3)
            c1, c2 = np.random.choice(range(box * 3, (box + 1) * 3), size=2)
            board[:, [c1, c2]] = board[:, [c2, c1]]
    solution = board.copy()
    board = delete(board, size, num)
    return board, solution


def delete(board: np.ndarray, size: int, num: int) -> np.ndarray:
    """
    Delete randomly the given number of unassigned position from a sudoku board
    :param board: The current solved sudoku board
    :param size: The size of the sudoku board
    :param num: The number of positions that should be removed
    :return: The sudoku board after removing some positions
    """
    for i in range(num):
        row = np.random.choice(size)
        col = np.random.choice(size)
        while board[row, col] == 0:
            row = np.random.choice(size)
            col = np.random.choice(size)
        board[row, col] = 0
    return board

pre_solved = np.array([[5, 3, 4, 6, 7, 8, 9, 1, 2],
                       [6, 7, 2, 1, 9, 5, 3, 4, 8],
                       [1, 9, 8, 3, 4, 2, 5, 6, 7],
                       [8, 5, 9, 7, 6, 1, 4, 2, 3],
                       [4, 2, 6, 8, 5, 3, 7, 9, 1],
                       [7, 1, 3, 9, 2, 4, 8, 5, 6],
                       [9, 6, 1, 5, 3, 7, 2, 8, 4],
                       [2, 8, 7, 4, 1, 9, 6, 3, 5],
                       [3, 4, 5, 2, 8, 6, 1, 7, 9]])