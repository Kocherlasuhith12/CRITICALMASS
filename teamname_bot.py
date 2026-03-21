"""
╔══════════════════════════════════════════════════════════╗
║   NeuralForge Bot v2 — Critical Mass: AI Bot Competition ║
║   IIT Patna | Chain Reaction on 12×8 board               ║
║   Strategy: Iterative Deepening Alpha-Beta Minimax       ║
║             + Opening Book + Smart Heuristics v2         ║
║   Author: Kocherla Koteswara Suhith Sravan Babu          ║
╚══════════════════════════════════════════════════════════╝
"""

import numpy as np
import time

# ─────────────────────────────────────────────────────────
# SECTION 1: CONSTANTS
# ─────────────────────────────────────────────────────────

ROWS       = 8
COLS       = 12
RED        = 1
GREEN      = 2
EMPTY      = 0
TIME_LIMIT = 0.85

# ─────────────────────────────────────────────────────────
# SECTION 2: PRECOMPUTED LOOKUP TABLES
# ─────────────────────────────────────────────────────────

CRITICAL_MASS = np.zeros((ROWS, COLS), dtype=np.int32)
for _r in range(ROWS):
    for _c in range(COLS):
        _n = 0
        if _r > 0:       _n += 1
        if _r < ROWS-1:  _n += 1
        if _c > 0:       _n += 1
        if _c < COLS-1:  _n += 1
        CRITICAL_MASS[_r][_c] = _n

NEIGHBORS = {}
for _r in range(ROWS):
    for _c in range(COLS):
        _nb = []
        if _r > 0:       _nb.append((_r-1, _c))
        if _r < ROWS-1:  _nb.append((_r+1, _c))
        if _c > 0:       _nb.append((_r, _c-1))
        if _c < COLS-1:  _nb.append((_r, _c+1))
        NEIGHBORS[(_r, _c)] = _nb

# ─────────────────────────────────────────────────────────
# SECTION 3: OPENING BOOK
# Corners have CM=2 — they explode fastest and are hardest
# to capture. Always claim them first. Zero search needed.
# ─────────────────────────────────────────────────────────

OPENING_BOOK = {
    RED:   [(0, 0), (7, 11), (0, 11), (7, 0)],
    GREEN: [(7, 11), (0, 0), (7, 0), (0, 11)],
}

def get_opening_move(owners, player, move_count):
    if move_count > 10:
        return None
    for (r, c) in OPENING_BOOK[player]:
        if owners[r][c] == EMPTY:
            return (r, c)
    return None

# ─────────────────────────────────────────────────────────
# SECTION 4: GAME STATE
# ─────────────────────────────────────────────────────────

def make_state():
    return (np.zeros((ROWS, COLS), dtype=np.int32),
            np.zeros((ROWS, COLS), dtype=np.int32))

# ─────────────────────────────────────────────────────────
# SECTION 5: APPLY MOVE + CHAIN EXPLOSION ENGINE
# ─────────────────────────────────────────────────────────

def apply_move(orbs, owners, row, col, player):
    orbs   = orbs.copy()
    owners = owners.copy()

    orbs[row][col]   += 1
    owners[row][col]  = player

    queue = []
    if orbs[row][col] >= CRITICAL_MASS[row][col]:
        queue.append((row, col))

    head = 0
    while head < len(queue):
        r, c  = queue[head]
        head += 1
        cm    = int(CRITICAL_MASS[r][c])
        if orbs[r][c] < cm:
            continue
        orbs[r][c] -= cm
        if orbs[r][c] == 0:
            owners[r][c] = EMPTY
        for (nr, nc) in NEIGHBORS[(r, c)]:
            orbs[nr][nc]   += 1
            owners[nr][nc]  = player
            if orbs[nr][nc] >= CRITICAL_MASS[nr][nc]:
                queue.append((nr, nc))

    return orbs, owners

# ─────────────────────────────────────────────────────────
# SECTION 6: GAME STATUS CHECKS
# ─────────────────────────────────────────────────────────

def get_winner(orbs, owners, move_count):
    if move_count < 4:
        return None
    has_red   = bool(np.any((owners == RED)   & (orbs > 0)))
    has_green = bool(np.any((owners == GREEN) & (orbs > 0)))
    if not has_red:
        return GREEN
    if not has_green:
        return RED
    return None

def get_valid_moves(owners, player):
    moves = []
    for r in range(ROWS):
        for c in range(COLS):
            o = owners[r][c]
            if o == EMPTY or o == player:
                moves.append((r, c))
    return moves

def get_game_phase(move_count, total_orbs):
    if move_count < 12:
        return 'opening'
    if total_orbs > 60:
        return 'endgame'
    return 'midgame'

# ─────────────────────────────────────────────────────────
# SECTION 7: HEURISTIC EVALUATION v2
# Phase-aware: opening / midgame / endgame modes
# Danger penalty: enemy near-critical cells threaten us
# Chain potential: reward cascades
# ─────────────────────────────────────────────────────────

def evaluate(orbs, owners, player, move_count):
    opponent = GREEN if player == RED else RED

    winner = get_winner(orbs, owners, move_count)
    if winner == player:
        return 100_000.0
    if winner == opponent:
        return -100_000.0

    score          = 0.0
    my_orbs_total  = 0
    opp_orbs_total = 0
    my_cells       = 0
    opp_cells      = 0
    my_critical    = 0
    opp_critical   = 0

    for r in range(ROWS):
        for c in range(COLS):
            owner = owners[r][c]
            n     = int(orbs[r][c])
            if n == 0:
                continue

            cm         = int(CRITICAL_MASS[r][c])
            pos_weight = 4 - cm
            ratio      = n / cm

            chain_potential = 0
            danger_exposure = 0

            for (nr, nc) in NEIGHBORS[(r, c)]:
                nb_owner = owners[nr][nc]
                nb_n     = int(orbs[nr][nc])
                nb_cm    = int(CRITICAL_MASS[nr][nc])
                if nb_owner == owner and nb_n >= nb_cm - 1:
                    chain_potential += 2
                if nb_owner not in (EMPTY, owner) and nb_n >= nb_cm - 1:
                    danger_exposure += 3

            stability  = pos_weight * 3
            cell_score = n * 1.0 + ratio * 4.0 + stability + chain_potential

            if owner == player:
                score          += cell_score - danger_exposure * 0.5
                my_orbs_total  += n
                my_cells       += 1
                if n >= cm:
                    my_critical += 1
            else:
                score          -= cell_score + danger_exposure * 0.5
                opp_orbs_total += n
                opp_cells      += 1
                if n >= cm:
                    opp_critical += 1

    total_orbs = my_orbs_total + opp_orbs_total
    phase      = get_game_phase(move_count, total_orbs)

    if phase == 'opening':
        score += (my_cells      - opp_cells)      * 2.0
        score += (my_orbs_total - opp_orbs_total) * 0.3
    elif phase == 'midgame':
        score += (my_cells      - opp_cells)      * 1.5
        score += (my_orbs_total - opp_orbs_total) * 0.5
        score += (my_critical   - opp_critical)   * 3.0
    else:  # endgame
        score += (my_orbs_total - opp_orbs_total) * 1.5
        score += (my_critical   - opp_critical)   * 5.0
        score += (my_cells      - opp_cells)      * 0.5

    return score

# ─────────────────────────────────────────────────────────
# SECTION 8: MOVE ORDERING v2
# ─────────────────────────────────────────────────────────

def order_moves(orbs, owners, moves, player):
    opponent = GREEN if player == RED else RED

    def quick_score(mv):
        r, c = mv
        n    = int(orbs[r][c])
        cm   = int(CRITICAL_MASS[r][c])
        s    = 0
        if n == cm - 1:
            s += 20
        elif n == cm - 2:
            s += 10
        for (nr, nc) in NEIGHBORS[(r, c)]:
            nb_n  = int(orbs[nr][nc])
            nb_cm = int(CRITICAL_MASS[nr][nc])
            if owners[nr][nc] == opponent:
                s += 5
                if nb_n >= nb_cm - 1:
                    s += 8
            if owners[nr][nc] == player and nb_n >= nb_cm - 1:
                s += 6
        s += (4 - cm) * 3
        return s

    return sorted(moves, key=quick_score, reverse=True)

# ─────────────────────────────────────────────────────────
# SECTION 9: ALPHA-BETA MINIMAX
# ─────────────────────────────────────────────────────────

class _Timeout(Exception):
    pass

def _alpha_beta(orbs, owners, depth, alpha, beta,
                is_maximizing, bot_player, move_count, deadline):

    if time.time() >= deadline:
        raise _Timeout()

    opponent   = GREEN if bot_player == RED else RED
    cur_player = bot_player if is_maximizing else opponent

    winner = get_winner(orbs, owners, move_count)
    if winner is not None:
        return (100_000.0 if winner == bot_player else -100_000.0), None

    if depth == 0:
        return evaluate(orbs, owners, bot_player, move_count), None

    moves = get_valid_moves(owners, cur_player)
    if not moves:
        return evaluate(orbs, owners, bot_player, move_count), None

    moves     = order_moves(orbs, owners, moves, cur_player)
    best_move = moves[0]

    if is_maximizing:
        best_val = -float('inf')
        for mv in moves:
            no, nw = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _ = _alpha_beta(no, nw, depth-1, alpha, beta,
                                 False, bot_player, move_count+1, deadline)
            if val > best_val:
                best_val  = val
                best_move = mv
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        best_val = float('inf')
        for mv in moves:
            no, nw = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _ = _alpha_beta(no, nw, depth-1, alpha, beta,
                                 True, bot_player, move_count+1, deadline)
            if val < best_val:
                best_val  = val
                best_move = mv
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val, best_move

# ─────────────────────────────────────────────────────────
# SECTION 10: ITERATIVE DEEPENING
# ─────────────────────────────────────────────────────────

def get_best_move(orbs, owners, player, move_count):
    # Step 1: Check opening book (instant)
    opening_mv = get_opening_move(owners, player, move_count)
    if opening_mv is not None:
        return opening_mv

    # Step 2: Iterative deepening Alpha-Beta
    deadline  = time.time() + TIME_LIMIT
    moves     = get_valid_moves(owners, player)

    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]

    best_move = order_moves(orbs, owners, moves, player)[0]

    for depth in range(1, 12):
        try:
            val, mv = _alpha_beta(
                orbs, owners, depth,
                -float('inf'), float('inf'),
                True, player, move_count, deadline
            )
            if mv is not None:
                best_move = mv
            if val >= 100_000.0:
                break
        except _Timeout:
            break

    return best_move

# ─────────────────────────────────────────────────────────
# SECTION 11: COMPETITION ENTRY POINT
# ─────────────────────────────────────────────────────────

def get_move(board, player, move_count=0):
    """
    Competition interface — called each turn.

    board = {
        'orbs':   2D list (8x12) — orb counts
        'owners': 2D list (8x12) — RED=1, GREEN=2, EMPTY=0
    }
    player     = RED (1) or GREEN (2)
    move_count = total moves played so far

    Returns: (row, col)
    """
    orbs   = np.array(board['orbs'],   dtype=np.int32)
    owners = np.array(board['owners'], dtype=np.int32)
    return get_best_move(orbs, owners, player, move_count)