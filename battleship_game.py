"""
Battleships game
=================

This module implements a simple command‑line version of the classic
Battleships game. The player competes against the computer on a grid of
their choosing, attempting to sink all of the computer's hidden ships
before running out of turns. The game is designed to satisfy the
learning objectives outlined in the Code Institute Python Essentials
project specification.

Features include:

* User‑definable grid size within reasonable bounds.
* Random placement of a configurable number of ships by the computer.
* Validation of all user input (grid size, row guesses and column guesses).
* Clear, user‑friendly feedback for hits, misses, repeated guesses and
  out‑of‑bounds entries.
* An ASCII board display that updates after every guess.

Throughout this module you'll find docstrings and inline comments to
describe what each function does. The code adheres to PEP 8 guidelines
for readability and style. Exception handling is used to gracefully
manage invalid input, ensuring a smooth user experience.
"""

from __future__ import annotations

import random
from typing import List, Set, Tuple


def create_board(size: int) -> List[List[str]]:
    """Return an empty game board represented as a 2D list.

    Each cell is initialised with a space (' ') character. The board
    uses zero‑based indexing internally, but user interactions assume
    one‑based row and column numbers.

    Args:
        size: The dimension of the square board (number of rows and columns).

    Returns:
        A list of lists containing strings.
    """
    return [[' ' for _ in range(size)] for _ in range(size)]


def place_ships(board_size: int, number_of_ships: int) -> Set[Tuple[int, int]]:
    """Randomly choose coordinates for a set of ships.

    The function ensures that ships do not overlap. Ships are
    represented by their (row, column) coordinates using zero‑based
    indexing. The number of ships should not exceed the total number
    of squares on the board.

    Args:
        board_size: The size of one side of the square board.
        number_of_ships: How many ships to place on the board.

    Returns:
        A set of tuples, each containing a row and column index.
    """
    if number_of_ships > board_size * board_size:
        # Break the error message across two lines to satisfy the flake8
        # maximum line length recommendation (79 characters per line).
        raise ValueError(
            "Number of ships cannot exceed the total number of squares "
            "on the board."
        )
    ships: Set[Tuple[int, int]] = set()
    while len(ships) < number_of_ships:
        row = random.randint(0, board_size - 1)
        col = random.randint(0, board_size - 1)
        ships.add((row, col))
    return ships


def display_board(
    board: List[List[str]],
    show_ships: bool = False,
    ships: Set[Tuple[int, int]] | None = None,
) -> None:
    """Print the current state of the game board to the console.

    Optionally reveal the positions of the remaining ships. The board is
    labelled with row numbers along the left side and column numbers
    along the top to aid the user in making guesses.

    Args:
        board: The 2D list representing the current state of the game.
        show_ships: If True, any unhit ships will be displayed as 'S'.
        ships: A set of ship positions. Required if `show_ships` is True.
    """
    size = len(board)
    # Column header
    header = "   " + " ".join(f"{col+1:>2}" for col in range(size))
    print(header)
    print("  " + "―" * (3 * size))
    for row_index, row in enumerate(board):
        row_display = f"{row_index + 1:>2}|"
        for col_index, cell in enumerate(row):
            # Reveal ships if requested and the cell hasn't been guessed.  The
            # conditional is broken across multiple lines to satisfy flake8's
            # maximum line length rule.
            if (
                show_ships
                and ships
                and (row_index, col_index) in ships
                and cell == ' '
            ):
                row_display += " S "
            else:
                row_display += f" {cell} "
        print(row_display)
    print()  # Blank line for spacing


def get_integer_input(prompt: str, min_value: int, max_value: int) -> int:
    """Prompt the user for an integer within a specified range.

    Continues to prompt until the user enters a valid integer between
    `min_value` and `max_value` inclusive. Handles non‑numeric input
    gracefully.

    Args:
        prompt: The message displayed to the user.
        min_value: The smallest allowable integer value.
        max_value: The largest allowable integer value.

    Returns:
        The validated integer input.
    """
    while True:
        user_input = input(prompt).strip()
        try:
            value = int(user_input)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if value < min_value or value > max_value:
            # Break the f-string onto two lines to satisfy line length limits
            print(
                f"Please enter a number between {min_value} "
                f"and {max_value}."
            )
            continue
        return value


def get_board_size() -> int:
    """Ask the user for their desired board size and validate the input.

    The board size is constrained to be between 4 and 10 inclusive. A
    smaller board becomes trivial and a larger board may become unwieldy
    for a command‑line interface.

    Returns:
        The chosen board size.
    """
    print("Choose your board size. It must be between 4 and 10.")
    return get_integer_input("Board size: ", 4, 10)


def get_number_of_ships(max_ships: int) -> int:
    """Prompt the user to select how many ships the computer should hide.

    The number of ships is constrained between 1 and `max_ships` inclusive.
    If the user selects too many ships, the game may be too difficult; too
    few ships may be too easy.

    Args:
        max_ships: The maximum allowable number of ships, typically less
            than or equal to half the number of squares on the board.

    Returns:
        The validated number of ships.
    """
    print(
        f"Choose how many ships to hide (between 1 and {max_ships})."
    )
    return get_integer_input("Number of ships: ", 1, max_ships)


def get_guess(size: int) -> Tuple[int, int]:
    """Prompt the user for a row and column guess within the board.

    The function continues to prompt until a valid pair of integers is
    entered. The returned values are zero‑based indices.

    Args:
        size: The size of one side of the square board.

    Returns:
        A tuple containing the row and column indices (zero‑based).
    """
    while True:
        print("Enter your guess (row and column).")
        row = get_integer_input(f"Row (1-{size}): ", 1, size) - 1
        col = get_integer_input(f"Column (1-{size}): ", 1, size) - 1
        return row, col


def update_board(
    board: List[List[str]], guess: Tuple[int, int], ships: Set[Tuple[int, int]]
) -> Tuple[bool, bool]:
    """Update the board based on the player's guess.

    Marks a hit with 'X' and a miss with 'O'. If the guess is a hit,
    the ship is removed from the `ships` set. The function returns
    whether the guess was a hit, and whether the cell had already been
    guessed previously.

    Args:
        board: The current state of the game board.
        guess: A tuple containing the guessed (row, col) indices.
        ships: A set of remaining ship positions.

    Returns:
        A tuple of booleans:
        - hit: True if the guess is a hit, False otherwise.
        - already_guessed: True if the cell was previously guessed.
    """
    row, col = guess
    cell_value = board[row][col]
    if cell_value in ('X', 'O'):
        # Player guessed this cell before
        return False, True
    if (row, col) in ships:
        board[row][col] = 'X'
        ships.remove((row, col))
        return True, False
    # It's a miss
    board[row][col] = 'O'
    return False, False


def game_loop() -> None:
    """Main loop controlling the flow of the battleship game.

    Handles initial setup (board size, number of ships, turn limit),
    repeatedly prompts the user for guesses, updates the game state, and
    checks for win/loss conditions. Ends when the player either sinks
    all ships or runs out of turns.
    """
    print("Welcome to Battleships!")
    size = get_board_size()

    # Limit the number of ships to roughly one quarter of the board
    max_possible_ships = (size * size) // 4
    if max_possible_ships < 1:
        max_possible_ships = 1
    num_ships = get_number_of_ships(max_possible_ships)

    board = create_board(size)
    ships = place_ships(size, num_ships)
    # Set number of turns.
    # Basic heuristic: twice the number of squares divided by number of ships.
    max_turns = max(size * size // num_ships, size)

    # Build a grammatically correct ship description. Breaking comments and
    # strings across lines ensures we adhere to flake8's maximum line length.
    ship_word = "ship" if num_ships == 1 else "ships"
    print(
        f"The computer has hidden {num_ships} {ship_word} on a "
        f"{size}×{size} board."
    )
    # Wrap the message onto two lines to conform to flake8's line length limit.
    print(
        f"You have {max_turns} turns to sink them all. Good luck!\n"
    )

    turns_taken = 0
    while turns_taken < max_turns and ships:
        print(f"Turn {turns_taken + 1} of {max_turns}")
        display_board(board)
        guess = get_guess(size)
        hit, already_guessed = update_board(board, guess, ships)
        if already_guessed:
            print("You already guessed that location. Try a different one.\n")
            # Do not count this as a turn
            continue
        if hit:
            print("Hit! You sunk a battleship!\n")
        else:
            print("Miss. No ship at that location.\n")
        turns_taken += 1
    # Game over conditions
    if not ships:
        print("Congratulations! You sank all the battleships!")
    else:
        print("Game over! You ran out of turns.")
        print(f"Ships remaining: {len(ships)}")
        display_board(board, show_ships=True, ships=ships)


if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
