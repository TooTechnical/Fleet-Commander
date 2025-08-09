"""
Flask web interface for the Battleships game.

This module provides a simple graphical (web‑based) front end for the
command‑line Battleships game implemented in ``battleship_game.py``.  It
allows players to configure the board size and number of ships via a
web form, and then play the game through a series of HTTP requests.

The application uses Flask for routing and rendering templates.  Game
state is stored in the user session, so multiple players can play
independently without interfering with each other.  You can deploy
this app to a platform like Heroku by including a ``Procfile`` and
``requirements.txt`` listing Flask and Gunicorn as dependencies.
"""

import os
from typing import List, Tuple

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from battleship_game import (
    create_board,
    place_ships,
    update_board,
)

app = Flask(__name__)
# Set a secret key for session encryption.  In production you should
# set the SECRET_KEY environment variable to a strong random value.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


def initialise_game(size: int, num_ships: int) -> None:
    """Initialise a new game and store it in the session.

    Args:
        size: The chosen board size.
        num_ships: How many ships to place on the board.
    """
    board = create_board(size)
    # Convert ship coordinates to lists for JSON serialisation
    ships = [list(coord) for coord in place_ships(size, num_ships)]
    # Determine turn limit (same heuristic as CLI version)
    max_turns = max(size * size // num_ships, size)
    session['game'] = {
        'board': board,
        'ships': ships,
        'size': size,
        'remaining_turns': max_turns,
    }


def load_game_from_session() -> Tuple[
    List[List[str]],
    List[List[int]],
    int,
    int,
]:
    """Retrieve the game state from the session.

    Returns:
        A tuple containing the board, ships (as list of [row, col]),
        board size and remaining turns.
    """
    game = session.get('game')
    if not game:
        return [], [], 0, 0
    board = game['board']
    ships = game['ships']
    size = game['size']
    remaining_turns = game['remaining_turns']
    return board, ships, size, remaining_turns


@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the home page where the user chooses board size and ships.

    On POST, initialises the game and redirects to the game page.
    """
    if request.method == 'POST':
        try:
            size = int(request.form.get('size', 0))
            num_ships = int(request.form.get('ships', 0))
        except ValueError:
            # If conversion fails, redisplay the form with an error. Break
            # arguments onto separate lines to satisfy flake8.
            return render_template(
                'index.html',
                error="Please enter valid numbers.",
            )
        # Validate size
        if size < 4 or size > 10:
            return render_template(
                'index.html',
                error="Board size must be between 4 and 10.",
            )
        # Limit ships to roughly one quarter of the board
        max_ships = (size * size) // 4 or 1
        if num_ships < 1 or num_ships > max_ships:
            return render_template(
                'index.html',
                error=(
                    f"Number of ships must be between 1 and {max_ships}."
                ),
            )
        # Set the battle type to sea unconditionally (land battles removed)
        battle_type = 'sea'
        country = request.form.get('country', 'USA')
        initialise_game(size, num_ships)
        # Store the battle type and country in the session
        session['game']['battle_type'] = battle_type
        session['game']['country'] = country
        return redirect(url_for('game'))
    return render_template('index.html')


@app.route('/game', methods=['GET', 'POST'])
def game():
    """Handle game play: display the board, accept guesses and update state.

    If no game is found in the session, redirects to the home page.
    """
    board, ships, size, remaining_turns = load_game_from_session()
    # Retrieve chosen battle type and country from session
    game_data = session.get('game', {})
    battle_type = game_data.get('battle_type', 'sea')
    country = game_data.get('country', '')
    if not board:
        return redirect(url_for('index'))

    message = ""
    endgame = False
    show_ships = False
    # Convert ships list of lists to a set of tuples for update logic
    ship_set = {tuple(coord) for coord in ships}

    if request.method == 'POST' and remaining_turns > 0 and ship_set:
        # Process guess
        try:
            row = int(request.form.get('row', 0)) - 1
            col = int(request.form.get('col', 0)) - 1
        except ValueError:
            message = "Invalid input. Please enter numbers for row and column."
        else:
            # Validate guess boundaries
            if row < 0 or row >= size or col < 0 or col >= size:
                message = f"Please choose numbers between 1 and {size}."
            else:
                hit, already_guessed = update_board(
                    board,
                    (row, col),
                    ship_set,
                )
                # Convert back to list of lists for session storage
                ships = [list(coord) for coord in ship_set]
                # Only deduct a turn if the guess wasn't repeated
                if not already_guessed:
                    remaining_turns -= 1
                    session['game']['remaining_turns'] = remaining_turns
                    # Record the last valid guess so it can be highlighted
                    # on the board
                    session['game']['last_guess'] = [row, col]
                session['game']['board'] = board
                session['game']['ships'] = ships
                # Mark session as modified so Flask saves nested changes
                session.modified = True
                if already_guessed:
                    message = "You already guessed that location. Try again."
                elif hit:
                    message = "Hit! You sank a battleship!"
                else:
                    message = "Miss. No ship at that location."

    # After processing, check for win/loss conditions
    if not ship_set:
        message = "Congratulations! You sank all the battleships!"
        endgame = True
        show_ships = True
    elif remaining_turns <= 0:
        message = "Game over! You ran out of turns."
        endgame = True
        show_ships = True

    # Pass the ships as a set of tuples for template checking
    ship_tuples: set[Tuple[int, int]] = {tuple(coord) for coord in ships}

    # Retrieve the last guess (if any) for highlighting
    last_guess = None
    lg = session['game'].get('last_guess')
    if isinstance(lg, list) and len(lg) == 2:
        last_guess = tuple(lg)

    return render_template(
        'game.html',
        board=board,
        size=size,
        message=message,
        remaining_turns=remaining_turns,
        endgame=endgame,
        show_ships=show_ships,
        ships=ship_tuples,
        battle_type=battle_type,
        country=country,
        last_guess=last_guess,
    )


if __name__ == '__main__':
    # Enable debug mode when running locally
    app.run(debug=True)
