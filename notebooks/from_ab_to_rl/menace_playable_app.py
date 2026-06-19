from __future__ import annotations

import json
from itertools import product
from typing import Any

import bokeh.events
import numpy as np
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.layouts import row as bokeh_row
from bokeh.models import Button, ColumnDataSource, CustomJS, Div
from bokeh.plotting import figure
from bokeh.resources import INLINE
from IPython.display import HTML, display
from matplotlib.colors import to_rgb
from menace_engine import (
    EMPTY,
    O_MARK,
    Board,
    MenaceEngine,
    X,
    available_actions,
    canonicalize_board,
    is_legal_reachable_board,
    is_terminal,
    player_to_move,
)

CELL_LABELS = (
    "top-left",
    "top-middle",
    "top-right",
    "middle-left",
    "center",
    "middle-right",
    "bottom-left",
    "bottom-middle",
    "bottom-right",
)

MOVE_CLASS_COLORS = (
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
    "#56B4E9",
    "#6B5B00",
    "#999999",
)

EMPTY_CELL_COLOR = "#f7f7f2"
HUMAN_MOVE_COLOR = "#eef4ff"
SAMPLED_MOVE_COLOR = "#fff4cf"
SAMPLED_BORDER_COLOR = "#c48a00"


def board_key(board: Board) -> str:
    """Serialize a board as a compact JavaScript lookup key."""
    return ",".join(str(value) for value in board)


def blend_with_white_hex(color: str, amount: float) -> str:
    """Return a lightened hex color for readable board overlays."""
    rgb = np.array(to_rgb(color))
    blended = (1.0 - amount) * np.ones(3) + amount * rgb
    return "#" + "".join(f"{round(channel * 255):02x}" for channel in blended)


def playable_groups_for_board(menace: MenaceEngine, board: Board) -> list[dict[str, Any]]:
    """Return display-ready symmetry-class data for one MENACE matchbox."""
    canonical_board, permutation = canonicalize_board(board)
    if canonical_board not in menace.boxes:
        return []

    beads = menace.boxes[canonical_board]
    total_beads = int(beads.sum())
    groups: list[dict[str, Any]] = []

    for action_index, canonical_action in enumerate(menace.matchbox_actions[canonical_board]):
        orbit = menace.matchbox_action_orbits[canonical_board][canonical_action]
        display_actions = sorted(int(permutation[action]) for action in orbit if board[permutation[action]] == EMPTY)
        if not display_actions:
            continue

        # This is the exact square MenaceEngine.choose_action would play after
        # sampling this canonical bead class. The other display actions are
        # symmetry-equivalent squares shown for interpretation only.
        representative = int(permutation[canonical_action])
        if representative not in display_actions:
            representative = display_actions[0]

        count = int(beads[action_index])
        color = MOVE_CLASS_COLORS[action_index % len(MOVE_CLASS_COLORS)]
        probability = count / total_beads if total_beads > 0 else 0.0
        groups.append(
            {
                "action_index": action_index,
                "representative": representative,
                "display_actions": display_actions,
                "count": count,
                "probability": probability,
                "color": color,
                "fill_color": blend_with_white_hex(color, 0.18),
                "label": CELL_LABELS[representative],
            }
        )

    groups.sort(key=lambda group: int(group["representative"]))
    return groups


def build_playable_policy_lookup(menace: MenaceEngine) -> dict[str, dict[str, Any]]:
    """Precompute trained MENACE policy data for all reachable X-to-move boards."""
    if menace.menace_mark != X:
        raise ValueError("The playable app expects an opening-player MENACE agent.")

    lookup: dict[str, dict[str, Any]] = {}
    for board in product((EMPTY, X, O_MARK), repeat=9):
        if not is_legal_reachable_board(board):
            continue
        if is_terminal(board):
            continue
        if player_to_move(board) != menace.menace_mark:
            continue
        if len(available_actions(board)) < 2:
            continue
        lookup[board_key(board)] = {"groups": playable_groups_for_board(menace=menace, board=board)}

    return lookup


def initial_board_source_data(groups: list[dict[str, Any]]) -> dict[str, list[Any]]:
    """Return initial board-cell glyph data for the empty board."""
    x_positions = [0.5, 1.5, 2.5, 0.5, 1.5, 2.5, 0.5, 1.5, 2.5]
    y_positions = [2.5, 2.5, 2.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5]
    data: dict[str, list[Any]] = {
        "x": x_positions,
        "y": y_positions,
        "count_y": [position + 0.28 for position in y_positions],
        "probability_y": [position + 0.13 for position in y_positions],
        "mark": [""] * 9,
        "mark_color": ["#222222"] * 9,
        "count_text": [""] * 9,
        "probability_text": [""] * 9,
        "info_color": ["#333333"] * 9,
        "fill_color": [EMPTY_CELL_COLOR] * 9,
        "policy_y": [position - 0.48 for position in y_positions],
        "policy_height": [0.0] * 9,
        "policy_fill_color": [EMPTY_CELL_COLOR] * 9,
        "line_color": ["#222222"] * 9,
        "line_width": [1.4] * 9,
    }

    for group in groups:
        policy_height = 0.96 * float(group["probability"])
        representative = int(group["representative"])
        data["fill_color"][representative] = group["fill_color"]
        data["policy_y"][representative] = data["y"][representative] - 0.48 + policy_height / 2
        data["policy_height"][representative] = policy_height
        data["policy_fill_color"][representative] = group["color"]
        data["line_color"][representative] = group["color"]
        data["count_text"][representative] = f"{group['count']} beads"
        data["probability_text"][representative] = f"p={group['probability']:.2f}"
        data["info_color"][representative] = group["color"]
        data["line_width"][representative] = 2.6

    return data


def show_inline_bokeh(model: Any) -> None:
    """Render one self-contained Bokeh view in a notebook output cell."""
    script, div = components(model)
    display(HTML(INLINE.render() + div + script))


def show_playable_menace_app(menace: MenaceEngine) -> None:
    """Display a browser-side app for playing O against a trained opening MENACE."""
    policy_lookup = build_playable_policy_lookup(menace)
    opening_board: Board = (EMPTY,) * 9
    opening_groups = policy_lookup[board_key(opening_board)]["groups"]

    board_source = ColumnDataSource(data=initial_board_source_data(opening_groups))
    lookup_source = ColumnDataSource(data={"payload": [json.dumps(policy_lookup, separators=(",", ":"))]})
    state_source = ColumnDataSource(data={"placeholder": []})

    board_plot = figure(
        x_range=(0, 3),
        y_range=(0, 3),
        width=430,
        height=430,
        toolbar_location=None,
        tools="",
        title="Play Against MENACE's Learned Policy",
    )
    board_plot.grid.visible = False
    board_plot.axis.visible = False
    board_plot.outline_line_width = 1.4
    board_plot.rect(
        x="x",
        y="y",
        width=0.98,
        height=0.98,
        fill_color="fill_color",
        line_color="line_color",
        line_width="line_width",
        source=board_source,
    )
    board_plot.rect(
        x="x",
        y="policy_y",
        width=0.9,
        height="policy_height",
        fill_color="policy_fill_color",
        fill_alpha=0.45,
        line_alpha=0.0,
        source=board_source,
    )
    board_plot.text(
        x="x",
        y="count_y",
        text="count_text",
        source=board_source,
        text_align="center",
        text_baseline="middle",
        text_font_size="9pt",
        text_font_style="bold",
        text_color="info_color",
    )
    board_plot.text(
        x="x",
        y="probability_y",
        text="probability_text",
        source=board_source,
        text_align="center",
        text_baseline="middle",
        text_font_size="9pt",
        text_color="info_color",
    )
    board_plot.text(
        x="x",
        y="y",
        text="mark",
        source=board_source,
        text_align="center",
        text_baseline="middle",
        text_font_size="34pt",
        text_font_style="bold",
        text_color="mark_color",
    )

    status_div = Div(
        text=(
            "<b>MENACE to move.</b> Colored squares show the symmetry-reduced matchbox policy. "
            "Vertical fill shows each bead-class probability. Labels show bead counts "
            "and normalized action probabilities. Click <b>Sample MENACE move</b> to draw one bead."
        ),
        width=520,
    )
    note_div = Div(
        text=(
            "You play <b>O</b>; MENACE plays <b>X</b>. This is a frozen trained policy: "
            "playing here does not add or remove beads."
        ),
        width=520,
    )
    button_menace_move = Button(label="Sample MENACE move", button_type="primary", width=180)
    button_reset = Button(label="Reset game", button_type="default", width=120)

    js_helpers = r"""
const CELL_LABELS = [
  'top-left', 'top-middle', 'top-right',
  'middle-left', 'center', 'middle-right',
  'bottom-left', 'bottom-middle', 'bottom-right'
];
const WIN_LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6]
];
const EMPTY_CELL_COLOR = '#f7f7f2';
const HUMAN_MOVE_COLOR = '#eef4ff';
const SAMPLED_MOVE_COLOR = '#fff4cf';
const SAMPLED_BORDER_COLOR = '#c48a00';

function ensureState() {
  if (!state_source._menace_play_app) {
    state_source._menace_play_app = {
      board: new Array(9).fill(0),
      lookup: JSON.parse(lookup_source.data.payload[0]),
      sampledAction: null,
    };
  }
  return state_source._menace_play_app;
}

function boardKey(board) {
  return board.join(',');
}

function availableActions(board) {
  const actions = [];
  for (let index = 0; index < board.length; index += 1) {
    if (board[index] === 0) {
      actions.push(index);
    }
  }
  return actions;
}

function winner(board) {
  for (const [a, b, c] of WIN_LINES) {
    if (board[a] !== 0 && board[a] === board[b] && board[a] === board[c]) {
      return board[a];
    }
  }
  return 0;
}

function isTerminal(board) {
  return winner(board) !== 0 || availableActions(board).length === 0;
}

function playerToMove(board) {
  let xCount = 0;
  let oCount = 0;
  for (const value of board) {
    if (value === 1) {
      xCount += 1;
    } else if (value === -1) {
      oCount += 1;
    }
  }
  return xCount === oCount ? 1 : -1;
}

function finalStatusHtml(board) {
  const winningMark = winner(board);
  if (winningMark === 1) {
    return '<b>Game over.</b> MENACE wins.';
  }
  if (winningMark === -1) {
    return '<b>Game over.</b> You win.';
  }
  return '<b>Game over.</b> The game ends in a draw.';
}

function getBoardEntry(state, board) {
  const legalActions = availableActions(board);
  if (legalActions.length === 1) {
    return {forcedAction: legalActions[0], groups: []};
  }
  return state.lookup[boardKey(board)] || {groups: []};
}

function applyPolicyFill(data, groups, showLabels) {
  let totalBeads = 0;
  for (const group of groups) {
    totalBeads += Number(group.count);
    const policyHeight = 0.96 * Number(group.probability);
    const representative = group.representative;
    data.fill_color[representative] = group.fill_color;
    data.policy_y[representative] = data.y[representative] - 0.48 + policyHeight / 2;
    data.policy_height[representative] = policyHeight;
    data.policy_fill_color[representative] = group.color;
    data.line_color[representative] = group.color;
    data.line_width[representative] = 1.8;
    if (showLabels) {
      data.count_text[representative] = `${group.count} beads`;
      data.probability_text[representative] = `p=${Number(group.probability).toFixed(2)}`;
      data.info_color[representative] = group.color;
      data.line_width[representative] = 2.8;
    }
  }
  return totalBeads;
}

function refreshDisplay(message) {
  const state = ensureState();
  const board = state.board;
  const data = board_source.data;

  for (let index = 0; index < 9; index += 1) {
    data.mark[index] = board[index] === 1 ? 'X' : (board[index] === -1 ? 'O' : '');
    data.mark_color[index] = board[index] === 1 ? '#222222' : '#7b3f00';
    data.count_text[index] = '';
    data.probability_text[index] = '';
    data.info_color[index] = '#333333';
    data.fill_color[index] = board[index] === 0 ? EMPTY_CELL_COLOR : '#ffffff';
    data.policy_y[index] = data.y[index] - 0.48;
    data.policy_height[index] = 0.0;
    data.policy_fill_color[index] = EMPTY_CELL_COLOR;
    data.line_color[index] = '#222222';
    data.line_width[index] = 1.4;
  }

  if (isTerminal(board)) {
    button_menace_move.disabled = true;
    status_div.text = message || finalStatusHtml(board);
  } else if (playerToMove(board) === 1) {
    const entry = getBoardEntry(state, board);
    if (entry.forcedAction !== undefined) {
      const action = entry.forcedAction;
      data.fill_color[action] = EMPTY_CELL_COLOR;
      data.policy_y[action] = data.y[action];
      data.policy_height[action] = 0.96;
      data.policy_fill_color[action] = '#999999';
      data.line_color[action] = '#555555';
      data.line_width[action] = 2.8;
      data.count_text[action] = 'forced';
      button_menace_move.label = 'Play forced move';
      button_menace_move.disabled = false;
      status_div.text = message || '<b>MENACE to move.</b> Only one legal move remains.';
    } else if (!entry.groups || entry.groups.length === 0) {
      button_menace_move.disabled = true;
      status_div.text = '<b>MENACE has no matchbox for this state.</b>';
    } else {
      const totalBeads = applyPolicyFill(data, entry.groups, true);
      if (state.sampledAction !== null) {
        data.fill_color[state.sampledAction] = SAMPLED_MOVE_COLOR;
        data.line_color[state.sampledAction] = SAMPLED_BORDER_COLOR;
        data.line_width[state.sampledAction] = 4.0;
      }
      button_menace_move.label = 'Sample MENACE move';
      button_menace_move.disabled = totalBeads <= 0;
      status_div.text = (
        message ||
        '<b>MENACE to move.</b> Colored squares show only symmetry-distinct bead classes.'
      );
    }
  } else {
    for (const action of availableActions(board)) {
      data.fill_color[action] = HUMAN_MOVE_COLOR;
      data.line_color[action] = '#6b83b5';
      data.line_width[action] = 1.8;
    }
    if (state.sampledAction !== null) {
      data.fill_color[state.sampledAction] = SAMPLED_MOVE_COLOR;
      data.line_color[state.sampledAction] = SAMPLED_BORDER_COLOR;
      data.line_width[state.sampledAction] = 4.0;
    }
    button_menace_move.label = 'Click board to play your move';
    button_menace_move.disabled = true;
    status_div.text = message || '<b>Your turn.</b> Click an empty square to play O.';
  }

  board_source.change.emit();
}

function sampleMenaceMove() {
  const state = ensureState();
  const board = state.board;
  if (isTerminal(board) || playerToMove(board) !== 1) {
    return;
  }

  const entry = getBoardEntry(state, board);
  let action = null;
  let sampledMessage = '';

  if (entry.forcedAction !== undefined) {
    action = entry.forcedAction;
    state.sampledRepresentative = action;
    sampledMessage = `MENACE played the only legal move: ${CELL_LABELS[action]}.`;
  } else {
    const groups = entry.groups || [];
    const totalBeads = groups.reduce((total, group) => total + Math.max(0, Number(group.count)), 0);
    if (totalBeads <= 0) {
      status_div.text = '<b>MENACE resigns.</b> This matchbox has no beads left.';
      button_menace_move.disabled = true;
      return;
    }

    let draw = Math.random() * totalBeads;
    let sampledGroup = groups[groups.length - 1];
    for (const group of groups) {
      draw -= Math.max(0, Number(group.count));
      if (draw <= 0) {
        sampledGroup = group;
        break;
      }
    }
    action = sampledGroup.representative;
    state.sampledRepresentative = sampledGroup.representative;
    sampledMessage = (
      `MENACE sampled the ${sampledGroup.label} bead class ` +
      `(${sampledGroup.count} beads, p=${Number(sampledGroup.probability).toFixed(2)}) ` +
      `and mapped it to ${CELL_LABELS[action]} on this board.`
    );
  }

  state.sampledAction = action;
  board[action] = 1;
  if (isTerminal(board)) {
    refreshDisplay(`${sampledMessage}<br>${finalStatusHtml(board)}`);
  } else {
    refreshDisplay(`${sampledMessage}<br><b>Your turn.</b> Click an empty square to play O.`);
  }
}

function handleBoardTap(event) {
  const state = ensureState();
  const board = state.board;
  if (isTerminal(board) || playerToMove(board) !== -1) {
    return;
  }
  const col = Math.floor(event.x);
  const row = 2 - Math.floor(event.y);
  if (row < 0 || row > 2 || col < 0 || col > 2) {
    return;
  }
  const action = row * 3 + col;
  if (board[action] !== 0) {
    return;
  }

  board[action] = -1;
  state.sampledAction = null;
  state.sampledRepresentative = null;
  if (isTerminal(board)) {
    refreshDisplay(`You played ${CELL_LABELS[action]}.<br>${finalStatusHtml(board)}`);
  } else {
    refreshDisplay(`You played ${CELL_LABELS[action]}.<br><b>MENACE to move.</b> Sample from the next matchbox.`);
  }
}

function resetGame() {
  const state = ensureState();
  state.board = new Array(9).fill(0);
  state.sampledAction = null;
  state.sampledRepresentative = null;
  refreshDisplay(
        '<b>MENACE to move.</b> Colored squares show only symmetry-distinct bead classes. ' +
        'Click <b>Sample MENACE move</b>.'
  );
}
"""

    callback_args = {
        "board_source": board_source,
        "lookup_source": lookup_source,
        "state_source": state_source,
        "status_div": status_div,
        "button_menace_move": button_menace_move,
    }
    button_menace_move.js_on_click(CustomJS(args=callback_args, code=f"{js_helpers}\nsampleMenaceMove();"))
    button_reset.js_on_click(CustomJS(args=callback_args, code=f"{js_helpers}\nresetGame();"))
    board_plot.js_on_event(
        bokeh.events.Tap,
        CustomJS(args=callback_args, code=f"{js_helpers}\nhandleBoardTap(cb_obj);"),
    )

    layout = column(
        note_div,
        board_plot,
        bokeh_row(button_menace_move, button_reset),
        status_div,
    )
    show_inline_bokeh(layout)
