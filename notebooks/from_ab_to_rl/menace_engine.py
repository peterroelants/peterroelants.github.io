from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Callable, TypeAlias

import numpy as np

Board: TypeAlias = tuple[int, ...]
OpponentPolicy: TypeAlias = Callable[[Board, int, np.random.Generator], int]

EMPTY = 0
X = 1
O_MARK = -1

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

# Each permutation lists the original square index that is copied into each new square.
SYMMETRY_PERMUTATIONS = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8),
    (6, 3, 0, 7, 4, 1, 8, 5, 2),
    (8, 7, 6, 5, 4, 3, 2, 1, 0),
    (2, 5, 8, 1, 4, 7, 0, 3, 6),
    (2, 1, 0, 5, 4, 3, 8, 7, 6),
    (6, 7, 8, 3, 4, 5, 0, 1, 2),
    (0, 3, 6, 1, 4, 7, 2, 5, 8),
    (8, 5, 2, 7, 4, 1, 6, 3, 0),
)

SYMMETRY_INVERSES = tuple(tuple(np.argsort(perm)) for perm in SYMMETRY_PERMUTATIONS)


def available_actions(board: Board) -> list[int]:
    """Return the empty squares on the board."""

    return [index for index, value in enumerate(board) if value == EMPTY]


def apply_action(board: Board, action: int, player_mark: int) -> Board:
    """Return the board obtained by placing a mark in one empty square."""

    next_board = list(board)
    next_board[action] = player_mark
    return tuple(next_board)


def winner(board: Board) -> int:
    """Return the winner of the board, or 0 if the game is still undecided."""

    for a, b, c in WIN_LINES:
        line = (board[a], board[b], board[c])
        if line == (X, X, X):
            return X
        if line == (O_MARK, O_MARK, O_MARK):
            return O_MARK
    return EMPTY


def is_terminal(board: Board) -> bool:
    """Return whether the game has ended in a win or a full board."""

    return winner(board) != EMPTY or all(value != EMPTY for value in board)


def player_to_move(board: Board) -> int:
    """Return the mark of the player whose turn it is on a legal board."""

    return X if board.count(X) == board.count(O_MARK) else O_MARK


def transform_board(board: Board, permutation: tuple[int, ...]) -> Board:
    """Apply one of the eight square symmetries to a board."""

    return tuple(board[index] for index in permutation)


def canonicalize_board(board: Board) -> tuple[Board, tuple[int, ...]]:
    """Return the lexicographically smallest symmetry-equivalent board and its permutation."""

    transformed = [(transform_board(board, permutation), permutation) for permutation in SYMMETRY_PERMUTATIONS]
    return min(transformed, key=lambda item: item[0])


def is_legal_reachable_board(board: Board) -> bool:
    """Return whether a board can occur in normal play with X moving first."""

    x_count = board.count(X)
    o_count = board.count(O_MARK)
    if x_count < o_count or x_count > o_count + 1:
        return False

    x_won = winner(board) == X
    o_won = winner(board) == O_MARK
    if x_won and o_won:
        return False
    if x_won and x_count != o_count + 1:
        return False
    if o_won and x_count != o_count:
        return False
    return True


def board_automorphisms(board: Board) -> list[tuple[int, ...]]:
    """Return the symmetries that leave the board unchanged."""

    return [
        inverse
        for permutation, inverse in zip(SYMMETRY_PERMUTATIONS, SYMMETRY_INVERSES, strict=False)
        if transform_board(board, permutation) == board
    ]


def representative_actions(board: Board) -> list[int]:
    """Return one canonical square index for each symmetry-distinct legal move."""

    automorphisms = board_automorphisms(board)
    remaining_actions = set(available_actions(board))
    representatives: list[int] = []

    while remaining_actions:
        action = min(remaining_actions)
        orbit = {inverse[action] for inverse in automorphisms}
        representatives.append(action)
        remaining_actions -= orbit

    return representatives


def enumerate_canonical_matchbox_boards(*, plays_first: bool) -> list[Board]:
    """Enumerate the symmetry-reduced non-terminal boards for which MENACE needs a choice."""

    menace_mark = X if plays_first else O_MARK
    matchbox_boards = set()

    for board in product((EMPTY, X, O_MARK), repeat=9):
        if not is_legal_reachable_board(board):
            continue
        if is_terminal(board):
            continue
        if player_to_move(board) != menace_mark:
            continue
        if len(available_actions(board)) < 2:
            continue
        matchbox_boards.add(canonicalize_board(board)[0])

    return sorted(matchbox_boards)


def find_winning_move(board: Board, player_mark: int) -> int | None:
    """Return an immediate winning move if one exists."""

    for action in available_actions(board):
        if winner(apply_action(board, action, player_mark)) == player_mark:
            return action
    return None


def count_immediate_wins(board: Board, player_mark: int) -> int:
    """Count the number of immediate winning moves from a board."""

    return sum(winner(apply_action(board, action, player_mark)) == player_mark for action in available_actions(board))


def find_fork_moves(board: Board, player_mark: int) -> list[int]:
    """Return moves that create two or more immediate wins on the next turn."""

    fork_moves = []
    for action in available_actions(board):
        next_board = apply_action(board, action, player_mark)
        if count_immediate_wins(next_board, player_mark) >= 2:
            fork_moves.append(action)
    return fork_moves


def random_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Choose a uniformly random legal move."""

    del player_mark
    return int(rng.choice(available_actions(board)))


def positional_heuristic_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Play immediate wins, then prefer center, corners, and finally sides."""

    action = find_winning_move(board, player_mark)
    if action is not None:
        return action

    if 4 in available_actions(board):
        return 4

    corners = [action for action in (0, 2, 6, 8) if action in available_actions(board)]
    if corners:
        return int(rng.choice(corners))

    return random_policy(board=board, player_mark=player_mark, rng=rng)


def defensive_heuristic_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Play immediate wins, block immediate losses, then prefer center, corners, and sides."""

    action = find_winning_move(board, player_mark)
    if action is not None:
        return action

    action = find_winning_move(board, -player_mark)
    if action is not None:
        return action

    if 4 in available_actions(board):
        return 4

    corners = [action for action in (0, 2, 6, 8) if action in available_actions(board)]
    if corners:
        return int(rng.choice(corners))

    return random_policy(board=board, player_mark=player_mark, rng=rng)


def simple_heuristic_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Backward-compatible name for the weaker positional heuristic."""

    return positional_heuristic_policy(board=board, player_mark=player_mark, rng=rng)


def fork_aware_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Play a fork-aware strategy that is stronger than the defensive heuristic but still imperfect."""

    action = find_winning_move(board, player_mark)
    if action is not None:
        return action

    action = find_winning_move(board, -player_mark)
    if action is not None:
        return action

    fork_moves = find_fork_moves(board, player_mark)
    if fork_moves:
        return int(rng.choice(fork_moves))

    opponent_forks = find_fork_moves(board, -player_mark)
    if len(opponent_forks) == 1:
        return opponent_forks[0]
    if len(opponent_forks) > 1 and 4 in available_actions(board):
        return 4

    if 4 in available_actions(board):
        return 4

    opposite_corners = (
        (0, 8),
        (2, 6),
        (6, 2),
        (8, 0),
    )
    for opponent_corner, my_corner in opposite_corners:
        if board[opponent_corner] == -player_mark and board[my_corner] == EMPTY:
            return my_corner

    corners = [action for action in (0, 2, 6, 8) if action in available_actions(board)]
    if corners:
        return int(rng.choice(corners))

    sides = [action for action in (1, 3, 5, 7) if action in available_actions(board)]
    return int(rng.choice(sides))


def strong_heuristic_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Play the standard rule-based tic-tac-toe strategy, which is effectively perfect."""

    action = find_winning_move(board, player_mark)
    if action is not None:
        return action

    action = find_winning_move(board, -player_mark)
    if action is not None:
        return action

    fork_moves = find_fork_moves(board, player_mark)
    if fork_moves:
        return int(rng.choice(fork_moves))

    opponent_forks = find_fork_moves(board, -player_mark)
    if len(opponent_forks) == 1:
        return opponent_forks[0]
    if len(opponent_forks) > 1:
        forcing_moves = []
        for action in available_actions(board):
            next_board = apply_action(board, action, player_mark)
            immediate_win = find_winning_move(next_board, player_mark)
            if immediate_win is not None and action not in opponent_forks:
                forcing_moves.append(action)
        if forcing_moves:
            return int(rng.choice(forcing_moves))

    if 4 in available_actions(board):
        return 4

    opposite_corners = (
        (0, 8),
        (2, 6),
        (6, 2),
        (8, 0),
    )
    for opponent_corner, my_corner in opposite_corners:
        if board[opponent_corner] == -player_mark and board[my_corner] == EMPTY:
            return my_corner

    corners = [action for action in (0, 2, 6, 8) if action in available_actions(board)]
    if corners:
        return int(rng.choice(corners))

    sides = [action for action in (1, 3, 5, 7) if action in available_actions(board)]
    return int(rng.choice(sides))


@lru_cache(maxsize=None)
def minimax_value(board: Board, player_mark: int) -> int:
    """Return the game-theoretic value from the current player's perspective."""

    winning_player = winner(board)
    if winning_player == player_mark:
        return 1
    if winning_player == -player_mark:
        return -1
    if all(value != EMPTY for value in board):
        return 0

    best_value = -2
    for action in available_actions(board):
        next_board = apply_action(board, action, player_mark)
        value = -minimax_value(next_board, -player_mark)
        if value > best_value:
            best_value = value
        if best_value == 1:
            break
    return best_value


def perfect_policy(board: Board, player_mark: int, rng: np.random.Generator) -> int:
    """Choose a minimax-optimal tic-tac-toe move."""

    del rng
    move_scores = []
    tie_break_priority = {4: 3, 0: 2, 2: 2, 6: 2, 8: 2, 1: 1, 3: 1, 5: 1, 7: 1}

    for action in available_actions(board):
        next_board = apply_action(board, action, player_mark)
        value = -minimax_value(next_board, -player_mark)
        move_scores.append((value, tie_break_priority[action], -action, action))

    move_scores.sort(reverse=True)
    return move_scores[0][-1]


@dataclass
class GameRecord:
    """A single played game from MENACE's perspective."""

    outcome: int
    final_board: Board
    resigned: bool


class MenaceEngine:
    """A symmetry-reduced MENACE implementation close to the original physical machine.

    Historical defaults follow the original matchbox construction:
    - opening player by default,
    - initial bead counts of 4, 3, 2, and 1 for the successive MENACE move stages,
    - reinforcement of +3 for a win, +1 for a draw, and -1 for a loss,
    - resignation if a used matchbox has no beads left.

    The class also supports a second-player variant for self-play and benchmarking.
    """

    def __init__(
        self,
        *,
        plays_first: bool = True,
        stage_beads: tuple[int, int, int, int] = (4, 3, 2, 1),
        win_reward: int = 3,
        draw_reward: int = 1,
        loss_reward: int = -1,
        rng: np.random.Generator | None = None,
    ) -> None:
        self.plays_first = plays_first
        self.menace_mark = X if plays_first else O_MARK
        self.opponent_mark = -self.menace_mark
        self.stage_beads = stage_beads
        self.win_reward = win_reward
        self.draw_reward = draw_reward
        self.loss_reward = loss_reward
        self.rng = rng if rng is not None else np.random.default_rng()

        self.matchbox_actions: dict[Board, list[int]] = {}
        self.matchbox_action_orbits: dict[Board, dict[int, set[int]]] = {}
        self.boxes: dict[Board, np.ndarray] = {}
        self.episode_history: list[tuple[Board, int]] = []

        for board in enumerate_canonical_matchbox_boards(plays_first=plays_first):
            actions = representative_actions(board)
            action_orbits = {
                action: {inverse[action] for inverse in board_automorphisms(board)} for action in actions
            }
            initial_beads = self.initial_beads_for_board(board)
            self.matchbox_actions[board] = actions
            self.matchbox_action_orbits[board] = action_orbits
            self.boxes[board] = np.full(len(actions), initial_beads, dtype=int)

    @property
    def matchbox_count(self) -> int:
        """Return the number of pre-built matchboxes in the engine."""

        return len(self.boxes)

    def initial_beads_for_board(self, board: Board) -> int:
        """Return the initial bead multiplicity for a board's MENACE move stage."""

        total_moves = board.count(X) + board.count(O_MARK)
        move_index = total_moves // 2 if self.plays_first else (total_moves - 1) // 2
        return self.stage_beads[move_index]

    def choose_action(self, board: Board, *, record_history: bool = True) -> int | None:
        """Sample a move from the board's matchbox, or return None if MENACE resigns."""

        legal_actions = available_actions(board)
        if len(legal_actions) == 1:
            return legal_actions[0]

        canonical_board, permutation = canonicalize_board(board)
        beads = self.boxes[canonical_board]
        if beads.sum() <= 0:
            return None

        probabilities = beads / beads.sum()
        action_index = int(self.rng.choice(len(probabilities), p=probabilities))
        canonical_action = self.matchbox_actions[canonical_board][action_index]
        original_action = permutation[canonical_action]

        if record_history:
            self.episode_history.append((canonical_board, action_index))

        return original_action

    def reinforce(self, outcome: int) -> None:
        """Update the visited matchboxes after a win (+1), draw (0), or loss (-1)."""

        delta = {1: self.win_reward, 0: self.draw_reward, -1: self.loss_reward}[outcome]
        for canonical_board, action_index in self.episode_history:
            updated = self.boxes[canonical_board][action_index] + delta
            self.boxes[canonical_board][action_index] = max(0, updated)
        self.episode_history.clear()

    def probability_grid(self, board: Board, *, spread_over_orbits: bool = False) -> np.ndarray:
        """Return the current action probabilities on the 3x3 board.

        When ``spread_over_orbits`` is true, the probability of a symmetry-distinct action
        is distributed evenly across all squares in that orbit. This is slightly less faithful
        to the physical machine, but it is often easier to visualize.
        """

        legal_actions = available_actions(board)
        if len(legal_actions) == 1:
            grid = np.zeros(9, dtype=float)
            grid[legal_actions[0]] = 1.0
            return grid.reshape(3, 3)

        canonical_board, permutation = canonicalize_board(board)
        beads = self.boxes[canonical_board]
        probabilities = beads / beads.sum()
        grid = np.zeros(9, dtype=float)

        for probability, canonical_action in zip(probabilities, self.matchbox_actions[canonical_board], strict=False):
            if not spread_over_orbits:
                grid[permutation[canonical_action]] = probability
                continue

            orbit = self.matchbox_action_orbits[canonical_board][canonical_action]
            original_orbit = [permutation[action] for action in orbit]
            for original_action in original_orbit:
                grid[original_action] += probability / len(original_orbit)

        return grid.reshape(3, 3)

    def reset_episode(self) -> None:
        """Discard any recorded moves from the current episode."""

        self.episode_history.clear()


def play_game_against_opponent(
    menace: MenaceEngine,
    opponent_policy: OpponentPolicy,
    *,
    learn: bool = True,
    rng: np.random.Generator | None = None,
) -> GameRecord:
    """Play one MENACE game against a fixed opponent policy."""

    game_rng = rng if rng is not None else menace.rng
    board: Board = (EMPTY,) * 9
    menace.reset_episode()
    resigned = False

    while True:
        if player_to_move(board) == menace.menace_mark:
            action = menace.choose_action(board, record_history=learn)
            if action is None:
                resigned = True
                outcome = -1
                break
            board = apply_action(board, action, menace.menace_mark)
        else:
            opponent_action = opponent_policy(board, menace.opponent_mark, game_rng)
            board = apply_action(board, opponent_action, menace.opponent_mark)

        if is_terminal(board):
            winning_player = winner(board)
            if winning_player == menace.menace_mark:
                outcome = 1
            elif winning_player == menace.opponent_mark:
                outcome = -1
            else:
                outcome = 0
            break

    if learn:
        menace.reinforce(outcome)
    else:
        menace.reset_episode()

    return GameRecord(outcome=outcome, final_board=board, resigned=resigned)


def play_self_play_game(
    opening_menace: MenaceEngine,
    reply_menace: MenaceEngine,
    *,
    learn: bool = True,
) -> tuple[GameRecord, GameRecord]:
    """Play one game between an opening-player MENACE and a second-player MENACE."""

    if not opening_menace.plays_first:
        raise ValueError("opening_menace must be configured as the opening player.")
    if reply_menace.plays_first:
        raise ValueError("reply_menace must be configured as the second player.")

    board: Board = (EMPTY,) * 9
    opening_menace.reset_episode()
    reply_menace.reset_episode()
    opening_resigned = False
    reply_resigned = False

    while True:
        x_action = opening_menace.choose_action(board, record_history=learn)
        if x_action is None:
            opening_resigned = True
            opening_outcome = -1
            reply_outcome = 1
            break
        board = apply_action(board, x_action, opening_menace.menace_mark)
        if is_terminal(board):
            winning_player = winner(board)
            opening_outcome = 1 if winning_player == opening_menace.menace_mark else 0
            reply_outcome = -1 if winning_player == opening_menace.menace_mark else 0
            break

        o_action = reply_menace.choose_action(board, record_history=learn)
        if o_action is None:
            reply_resigned = True
            opening_outcome = 1
            reply_outcome = -1
            break
        board = apply_action(board, o_action, reply_menace.menace_mark)
        if is_terminal(board):
            winning_player = winner(board)
            reply_outcome = 1 if winning_player == reply_menace.menace_mark else 0
            opening_outcome = -1 if winning_player == reply_menace.menace_mark else 0
            break

    if learn:
        opening_menace.reinforce(opening_outcome)
        reply_menace.reinforce(reply_outcome)
    else:
        opening_menace.reset_episode()
        reply_menace.reset_episode()

    return (
        GameRecord(outcome=opening_outcome, final_board=board, resigned=opening_resigned),
        GameRecord(outcome=reply_outcome, final_board=board, resigned=reply_resigned),
    )


def summarize_outcomes(outcomes: list[int]) -> dict[str, float]:
    """Convert win/draw/loss outcomes into proportions."""

    outcome_array = np.array(outcomes, dtype=int)
    return {
        "win": float(np.mean(outcome_array == 1)),
        "draw": float(np.mean(outcome_array == 0)),
        "loss": float(np.mean(outcome_array == -1)),
    }


def evaluate_against_opponent(
    menace: MenaceEngine,
    opponent_policy: OpponentPolicy,
    *,
    n_games: int = 2_000,
    seed: int = 0,
) -> dict[str, float]:
    """Evaluate a fixed MENACE agent without further learning."""

    rng = np.random.default_rng(seed)
    outcomes = [
        play_game_against_opponent(menace, opponent_policy, learn=False, rng=rng).outcome for _ in range(n_games)
    ]
    return summarize_outcomes(outcomes)
