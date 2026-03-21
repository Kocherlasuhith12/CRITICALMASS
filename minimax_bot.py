"""
minimax_bot.py — Depth-2 Minimax opponent bot
Strategy: Basic Minimax at fixed depth 2. No Alpha-Beta pruning.
This represents the ceiling of what most CS students implement
in a competition week. A tough but beatable opponent.
"""

from neuralforge_bot import (
    ROWS, COLS, RED, GREEN, EMPTY,
    CRITICAL_MASS, NEIGHBORS,
    make_state, apply_move, get_winner, get_valid_moves,
    count_orbs, count_cells
)

SEARCH_DEPTH = 2


def minimax_evaluate(orbs, owners, player, move_count):
    """Simple heuristic — orb count + cell count advantage."""
    opponent = GREEN if player == RED else RED

    winner = get_winner(orbs, owners, move_count)
    if winner == player:   return 50_000
    if winner == opponent: return -50_000

    my_orbs   = count_orbs(orbs, owners, player)
    opp_orbs  = count_orbs(orbs, owners, opponent)
    my_cells  = count_cells(owners, player)
    opp_cells = count_cells(owners, opponent)

    # Near-critical bonus
    near_crit_me  = 0
    near_crit_opp = 0
    for r in range(ROWS):
        for c in range(COLS):
            n  = int(orbs[r][c])
            cm = int(CRITICAL_MASS[r][c])
            if owners[r][c] == player   and n == cm - 1: near_crit_me  += 1
            if owners[r][c] == opponent and n == cm - 1: near_crit_opp += 1

    return (
        (my_orbs   - opp_orbs)  * 1.0
        + (my_cells  - opp_cells) * 1.5
        + (near_crit_me - near_crit_opp) * 2.0
    )


def minimax(orbs, owners, depth, is_maximizing, player, move_count):
    """Plain Minimax — no Alpha-Beta, fixed depth."""
    opponent   = GREEN if player == RED else RED
    cur_player = player if is_maximizing else opponent

    winner = get_winner(orbs, owners, move_count)
    if winner is not None:
        return (50_000 if winner == player else -50_000), None

    if depth == 0:
        return minimax_evaluate(orbs, owners, player, move_count), None

    moves = get_valid_moves(owners, cur_player)
    if not moves:
        return minimax_evaluate(orbs, owners, player, move_count), None

    best_move = moves[0]

    if is_maximizing:
        best_val = -float('inf')
        for mv in moves:
            no, nw = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _ = minimax(no, nw, depth-1, False, player, move_count+1)
            if val > best_val:
                best_val  = val
                best_move = mv
        return best_val, best_move
    else:
        best_val = float('inf')
        for mv in moves:
            no, nw = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _ = minimax(no, nw, depth-1, True, player, move_count+1)
            if val < best_val:
                best_val  = val
                best_move = mv
        return best_val, best_move


def get_move(orbs, owners, player, move_count=0):
    """Minimax depth-2: strongest typical student submission."""
    import time
    moves = get_valid_moves(owners, player)
    if not moves:
        return None

    # Safety: if too many moves, cap search to avoid timeout
    if len(moves) > 40:
        # Quick greedy fallback on first few moves
        from greedy_bot import get_move as greedy_mv
        return greedy_mv(orbs, owners, player, move_count)

    _, mv = minimax(orbs, owners, SEARCH_DEPTH, True, player, move_count)
    return mv