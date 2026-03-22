"""
greedy_bot.py — Greedy opponent bot
Strategy: Always picks the move with the highest IMMEDIATE score.
No lookahead. No search. Just instant gratification.
This is what most beginner students submit.
"""

from NeuralForge_bot import (
    ROWS, COLS, RED, GREEN, EMPTY,
    CRITICAL_MASS, NEIGHBORS,
    make_state, apply_move, get_winner, get_valid_moves, count_orbs
)


def greedy_score(orbs, owners, row, col, player):
    """
    Score a move by how much it immediately improves the board.
    Factors: orbs gained, cells captured, near-critical bonus.
    """
    opponent = GREEN if player == RED else RED

    new_orbs, new_owners = apply_move(orbs, owners, row, col, player)

    my_orbs_before  = count_orbs(orbs, owners, player)
    my_orbs_after   = count_orbs(new_orbs, new_owners, player)
    opp_orbs_before = count_orbs(orbs, owners, opponent)
    opp_orbs_after  = count_orbs(new_orbs, new_owners, opponent)

    # Orbs gained + opponent orbs lost
    score = (my_orbs_after - my_orbs_before) + (opp_orbs_before - opp_orbs_after) * 2

    # Bonus: cells we now own that we didn't before
    for r in range(ROWS):
        for c in range(COLS):
            if new_owners[r][c] == player and owners[r][c] != player:
                score += 3

    return score


def get_move(orbs, owners, player, move_count=0):
    """Greedy: pick the move with highest immediate score."""
    moves = get_valid_moves(owners, player)
    if not moves:
        return None

    best_move  = moves[0]
    best_score = -float('inf')

    for mv in moves:
        s = greedy_score(orbs, owners, mv[0], mv[1], player)
        if s > best_score:
            best_score = s
            best_move  = mv

    return best_move