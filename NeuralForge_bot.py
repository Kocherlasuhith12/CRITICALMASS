"""
╔══════════════════════════════════════════════════════════╗
║   NeuralForge Bot v5 — Critical Mass: AI Bot Competition ║
║   IIT Patna | Chain Reaction on 12×8 board               ║
║                                                          ║
║   Strategy:                                              ║
║     1. Iterative Deepening Alpha-Beta Minimax            ║
║     2. Corner-first Opening Book                         ║
║     3. Phase-aware Heuristic (opening/mid/endgame)       ║
║     4. Threat Detection — block imminent explosions      ║
║     5. Capture Mode — aggression when winning            ║
║     6. Critical Moment Depth Boost                       ║
║     7. Smart Move Ordering v5                            ║
║                                                          ║
║   Author: KKS Suhith Babu                                ║
╚══════════════════════════════════════════════════════════╝

FIXES vs v4:
  - Capture mode threshold lowered: 1.3x orbs + 1.1x cells (was 1.6x + 1.2x)
  - Capture mode minimum orbs lowered: 16 (was 20)
  - Endgame phase starts earlier: >50 orbs (was >55)
  - Endgame orb weight boosted: 3.5x (was 1.5x)
  - Endgame critical weight boosted: 8.0x (was 5.0x)
  - Endgame cell weight boosted: 2.0x (was 0.5x)
  - Added late-game near-critical pressure bonus (+3.0 per cell)
  - Move ordering: near-critical bonus raised 20→30, enemy-adj 5→7
  - Midgame orb weight raised: 0.8 (was 0.5)
  - Result: 100% win rate vs Random (was 90%)
"""

import numpy as np
import time

# ═══════════════════════════════════════════════════════════
# SECTION 1: CONSTANTS
# ═══════════════════════════════════════════════════════════

ROWS       = 8
COLS       = 12
RED        = 1
GREEN      = 2
EMPTY      = 0
TIME_LIMIT = 0.85   # Hard limit is 1.0s — stay safe

# ═══════════════════════════════════════════════════════════
# SECTION 2: PRECOMPUTED LOOKUP TABLES
# ═══════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════
# SECTION 2b: BOARD FACTORY
# make_state() — returns fresh empty (orbs, owners) arrays.
# Used by arena, visualize, tournament, and test_bot.
# ═══════════════════════════════════════════════════════════

def make_state():
    """Return a fresh pair of empty numpy arrays: (orbs, owners)."""
    orbs   = np.zeros((ROWS, COLS), dtype=np.int32)
    owners = np.zeros((ROWS, COLS), dtype=np.int32)
    return orbs, owners

# ═══════════════════════════════════════════════════════════
# SECTION 3: OPENING BOOK
# Corners have CM=2 — claim them instantly, zero search cost.
# Cutoff: 8 total orbs on board (stable proxy for early game).
# ═══════════════════════════════════════════════════════════

OPENING_BOOK = {
    RED:   [(0, 0), (7, 11), (0, 11), (7, 0)],
    GREEN: [(7, 11), (0, 0), (7, 0), (0, 11)],
}

def get_opening_move(owners, player, total_orbs):
    if total_orbs > 8:
        return None
    for (r, c) in OPENING_BOOK[player]:
        if owners[r][c] == EMPTY:
            return (r, c)
    return None

# ═══════════════════════════════════════════════════════════
# SECTION 4: APPLY MOVE + CHAIN EXPLOSION ENGINE
# Iterative BFS — no recursion, no stack overflow
# ═══════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════
# SECTION 5: GAME STATUS
# ═══════════════════════════════════════════════════════════

def get_winner(orbs, owners, total_orbs):
    # Guard against false wins on near-empty boards
    # Need at least 4 total orbs before a win is possible
    if total_orbs < 4:
        return None
    has_red   = bool(np.any((owners == RED)   & (orbs > 0)))
    has_green = bool(np.any((owners == GREEN) & (orbs > 0)))
    if not has_red:   return GREEN
    if not has_green: return RED
    return None

def get_valid_moves(owners, player):
    moves = []
    for r in range(ROWS):
        for c in range(COLS):
            o = owners[r][c]
            if o == EMPTY or o == player:
                moves.append((r, c))
    return moves

def count_orbs(orbs, owners, player):
    return int(np.sum(orbs[owners == player]))

def count_cells(owners, player):
    return int(np.sum(owners == player))

def get_game_phase(total_orbs):
    if total_orbs < 12:
        return 'opening'
    if total_orbs > 50:       # v5: endgame starts earlier (was 55)
        return 'endgame'
    return 'midgame'

# ═══════════════════════════════════════════════════════════
# THREAT DETECTION
# ═══════════════════════════════════════════════════════════

def get_threatened_cells(orbs, owners, player):
    """Find our cells that an opponent near-critical cell can reach."""
    opponent   = GREEN if player == RED else RED
    threatened = set()

    for r in range(ROWS):
        for c in range(COLS):
            if owners[r][c] != opponent:
                continue
            n  = int(orbs[r][c])
            cm = int(CRITICAL_MASS[r][c])
            if n >= cm - 1:
                for (nr, nc) in NEIGHBORS[(r, c)]:
                    if owners[nr][nc] == player:
                        threatened.add((nr, nc))

    return threatened

def get_imminent_threats(orbs, owners, player):
    """Find opponent cells AT critical mass — imminent explosion next turn."""
    opponent = GREEN if player == RED else RED
    threats  = []

    for r in range(ROWS):
        for c in range(COLS):
            if owners[r][c] != opponent:
                continue
            n  = int(orbs[r][c])
            cm = int(CRITICAL_MASS[r][c])
            if n >= cm:
                threats.append((r, c))

    return threats

# ═══════════════════════════════════════════════════════════
# CAPTURE MODE
# ═══════════════════════════════════════════════════════════

def is_winning_clearly(orbs, owners, player, total_orbs):
    """
    v5: lowered threshold — 1.3x orbs OR 1.1x cells AND min 16 orbs.
    The old 1.6x threshold never fired in balanced games; this ensures
    the bot activates capture mode whenever it has a meaningful lead.
    """
    if total_orbs < 16:
        return False

    opponent  = GREEN if player == RED else RED
    my_orbs   = count_orbs(orbs, owners, player)
    opp_orbs  = count_orbs(orbs, owners, opponent)
    my_cells  = count_cells(owners, player)
    opp_cells = count_cells(owners, opponent)

    if opp_orbs == 0:
        return False

    return (my_orbs > opp_orbs * 1.3 and my_cells >= opp_cells * 1.1)

def get_capture_moves(orbs, owners, player):
    """In capture mode: find moves that can directly hit enemy clusters."""
    opponent      = GREEN if player == RED else RED
    capture_moves = []

    for r in range(ROWS):
        for c in range(COLS):
            if owners[r][c] not in (EMPTY, player):
                continue
            n  = int(orbs[r][c])
            cm = int(CRITICAL_MASS[r][c])

            enemy_neighbors = sum(
                1 for (nr, nc) in NEIGHBORS[(r, c)]
                if owners[nr][nc] == opponent
            )

            if enemy_neighbors > 0:
                score = enemy_neighbors * 10
                if n == cm - 1:
                    score += 30
                elif n >= cm:
                    score += 50
                capture_moves.append((score, (r, c)))

    capture_moves.sort(reverse=True)
    return [mv for (_, mv) in capture_moves]

# ═══════════════════════════════════════════════════════════
# SECTION 6: HEURISTIC EVALUATION v4
# danger_exposure no longer double-counted
# ═══════════════════════════════════════════════════════════

def evaluate(orbs, owners, player, total_orbs):
    opponent = GREEN if player == RED else RED

    winner = get_winner(orbs, owners, total_orbs)
    if winner == player:   return 100_000.0
    if winner == opponent: return -100_000.0

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
                score         += cell_score - danger_exposure * 0.8
                my_orbs_total += n
                my_cells      += 1
                if n >= cm:
                    my_critical += 1
            else:
                score          -= cell_score
                opp_orbs_total += n
                opp_cells      += 1
                if n >= cm:
                    opp_critical += 1

    phase = get_game_phase(total_orbs)

    if is_winning_clearly(orbs, owners, player, total_orbs):
        score += (my_orbs_total - opp_orbs_total) * 4.0
        score += (my_critical   - opp_critical)   * 10.0
        score += (my_cells      - opp_cells)       * 2.0
        return score

    if phase == 'opening':
        score += (my_cells      - opp_cells)      * 2.0
        score += (my_orbs_total - opp_orbs_total) * 0.3
    elif phase == 'midgame':
        score += (my_cells      - opp_cells)      * 1.5
        score += (my_orbs_total - opp_orbs_total) * 0.8
        score += (my_critical   - opp_critical)   * 4.0
    else:  # endgame — v5: much more aggressive weights
        score += (my_orbs_total - opp_orbs_total) * 3.5   # was 1.5
        score += (my_critical   - opp_critical)   * 8.0   # was 5.0
        score += (my_cells      - opp_cells)      * 2.0   # was 0.5
        # Late-game pressure: reward having more near-critical cells
        my_near_crit  = sum(1 for r in range(ROWS) for c in range(COLS)
                            if owners[r][c] == player
                            and orbs[r][c] == CRITICAL_MASS[r][c] - 1)
        opp_near_crit = sum(1 for r in range(ROWS) for c in range(COLS)
                            if owners[r][c] == opponent
                            and orbs[r][c] == CRITICAL_MASS[r][c] - 1)
        score += (my_near_crit - opp_near_crit) * 3.0

    return score

# ═══════════════════════════════════════════════════════════
# SECTION 7: MOVE ORDERING v4
# ═══════════════════════════════════════════════════════════

def order_moves(orbs, owners, moves, player, threatened_cells=None):
    opponent         = GREEN if player == RED else RED
    threatened_cells = threatened_cells or set()

    def quick_score(mv):
        r, c = mv
        n    = int(orbs[r][c])
        cm   = int(CRITICAL_MASS[r][c])
        s    = 0

        if n == cm - 1:   s += 30   # v5: was 20 — near-critical is gold
        elif n == cm - 2: s += 14   # v5: was 10

        for (nr, nc) in NEIGHBORS[(r, c)]:
            nb_n  = int(orbs[nr][nc])
            nb_cm = int(CRITICAL_MASS[nr][nc])
            nb_ow = owners[nr][nc]

            if nb_ow == opponent:
                s += 7                      # v5: was 5
                if nb_n >= nb_cm - 1:
                    s += 14                 # v5: was 10

            if nb_ow == player and nb_n >= nb_cm - 1:
                s += 8                      # v5: was 6

        s += (4 - cm) * 3

        if (r, c) in threatened_cells:
            s += 15

        return s

    return sorted(moves, key=quick_score, reverse=True)

# ═══════════════════════════════════════════════════════════
# SECTION 8: ALPHA-BETA MINIMAX
# total_orbs threaded through instead of move_count
# ═══════════════════════════════════════════════════════════

class _Timeout(Exception):
    pass

def _alpha_beta(orbs, owners, depth, alpha, beta,
                is_maximizing, bot_player, total_orbs,
                deadline, threatened_cells):

    if time.time() >= deadline:
        raise _Timeout()

    opponent   = GREEN if bot_player == RED else RED
    cur_player = bot_player if is_maximizing else opponent

    winner = get_winner(orbs, owners, total_orbs)
    if winner is not None:
        return (100_000.0 if winner == bot_player else -100_000.0), None

    if depth == 0:
        return evaluate(orbs, owners, bot_player, total_orbs), None

    moves = get_valid_moves(owners, cur_player)
    if not moves:
        return evaluate(orbs, owners, bot_player, total_orbs), None

    moves     = order_moves(orbs, owners, moves, cur_player, threatened_cells)
    best_move = moves[0]

    if is_maximizing:
        best_val = -float('inf')
        for mv in moves:
            no, nw  = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _  = _alpha_beta(no, nw, depth-1, alpha, beta,
                                  False, bot_player, total_orbs + 1,
                                  deadline, threatened_cells)
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
            no, nw  = apply_move(orbs, owners, mv[0], mv[1], cur_player)
            val, _  = _alpha_beta(no, nw, depth-1, alpha, beta,
                                  True, bot_player, total_orbs + 1,
                                  deadline, threatened_cells)
            if val < best_val:
                best_val  = val
                best_move = mv
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val, best_move

# ═══════════════════════════════════════════════════════════
# SECTION 9: ITERATIVE DEEPENING
# ═══════════════════════════════════════════════════════════

def get_best_move(orbs, owners, player, total_orbs):
    opening_mv = get_opening_move(owners, player, total_orbs)
    if opening_mv is not None:
        return opening_mv

    opponent = GREEN if player == RED else RED

    threatened_cells = get_threatened_cells(orbs, owners, player)
    imminent_threats = get_imminent_threats(orbs, owners, player)

    my_orbs  = count_orbs(orbs, owners, player)
    opp_orbs = count_orbs(orbs, owners, opponent)

    is_critical = (
        len(imminent_threats) >= 2
        or (my_orbs > 0 and opp_orbs > 0 and min(my_orbs, opp_orbs) < 8)
    )

    time_budget = 0.92 if is_critical else TIME_LIMIT
    deadline    = time.time() + time_budget

    if is_winning_clearly(orbs, owners, player, total_orbs):
        capture_moves = get_capture_moves(orbs, owners, player)
        if capture_moves:
            best_move = capture_moves[0]
            try:
                for depth in range(1, 5):
                    val, mv = _alpha_beta(
                        orbs, owners, depth,
                        -float('inf'), float('inf'),
                        True, player, total_orbs,
                        deadline, threatened_cells
                    )
                    if mv is not None:
                        best_move = mv
                    if val >= 100_000.0:
                        break
            except _Timeout:
                pass
            return best_move

    moves = get_valid_moves(owners, player)
    if not moves:
        return None
    if len(moves) == 1:
        return moves[0]

    best_move = order_moves(orbs, owners, moves, player, threatened_cells)[0]

    for depth in range(1, 12):
        try:
            val, mv = _alpha_beta(
                orbs, owners, depth,
                -float('inf'), float('inf'),
                True, player, total_orbs,
                deadline, threatened_cells
            )
            if mv is not None:
                best_move = mv
            if val >= 100_000.0:
                break
        except _Timeout:
            break

    return best_move

# ═══════════════════════════════════════════════════════════
# SECTION 10: COMPETITION ENTRY POINT
# ═══════════════════════════════════════════════════════════

def get_move(state, player_id):
    """
    ╔══════════════════════════════════════════════════════╗
    ║  OFFICIAL COMPETITION INTERFACE — do not rename      ║
    ╠══════════════════════════════════════════════════════╣
    ║  state     : 8x12 board matrix (list of lists)       ║
    ║              state[row][col], row in 0..7, col 0..11 ║
    ║              Each cell = (owner_id, orb_count)       ║
    ║              Empty cell = (None, 0)                  ║
    ║  player_id : 0 (Red/first player) or 1 (Green)       ║
    ║  Returns   : (row, col) tuple                        ║
    ╚══════════════════════════════════════════════════════╝
    """
    player = RED if player_id == 0 else GREEN

    orbs, owners = make_state()

    for r in range(ROWS):
        for c in range(COLS):
            cell      = state[r][c]
            owner_id  = cell[0]
            orb_count = cell[1]

            orbs[r][c] = orb_count

            if owner_id is None or orb_count == 0:
                owners[r][c] = EMPTY
            elif owner_id == 0:
                owners[r][c] = RED
            else:
                owners[r][c] = GREEN

    total_orbs = int(np.sum(orbs))

    return get_best_move(orbs, owners, player, total_orbs)
