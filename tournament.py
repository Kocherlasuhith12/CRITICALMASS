"""
tournament.py — Full tournament: NeuralForge vs all opponents
Tests our bot against 3 opponent types with detailed stats.
Usage: python3 tournament.py
"""

import random, time, sys
import numpy as np

from NeuralForge_bot import (
    ROWS, COLS, RED, GREEN, EMPTY,
    make_state, apply_move, get_winner,
    get_valid_moves, get_best_move, count_orbs
)
import greedy_bot
import minimax_bot

# ── Config ──────────────────────────────────────────────
GAMES_PER_MATCHUP = 5     # raise to 10+ for more accuracy
MAX_TURNS         = 120   # cap for speed; winner by orb count if no elim
NEURALFORGE_TIME  = 0.1   # use 0.85 for full-strength test (slow)

# ── Helpers ─────────────────────────────────────────────

def random_move(owners, player):
    moves = get_valid_moves(owners, player)
    return random.choice(moves) if moves else None

def orb_winner(orbs, owners):
    """Who has more orbs — used when turn limit reached."""
    r = count_orbs(orbs, owners, RED)
    g = count_orbs(orbs, owners, GREEN)
    if r > g: return RED
    if g > r: return GREEN
    return None   # exact tie

def play_game(neuralforge_player, opponent_get_move, label):
    """
    Play one game. NeuralForge is neuralforge_player (RED or GREEN).
    opponent_get_move(orbs, owners, player, total_orbs) -> (r,c)
    Returns (winner, turns, margin)
    """
    orbs, owners = make_state()
    current      = RED

    for turn in range(MAX_TURNS):
        total_orbs = int(np.sum(orbs))

        w = get_winner(orbs, owners, total_orbs)
        if w:
            margin = count_orbs(orbs, owners, w) - count_orbs(orbs, owners,
                     GREEN if w == RED else RED)
            return w, turn, margin

        if current == neuralforge_player:
            mv = get_best_move(orbs, owners, current, total_orbs)
        else:
            mv = opponent_get_move(orbs, owners, current, total_orbs)

        if mv is None:
            break
        orbs, owners = apply_move(orbs, owners, mv[0], mv[1], current)
        current = GREEN if current == RED else RED

    w = orb_winner(orbs, owners)
    nf_orbs  = count_orbs(orbs, owners, neuralforge_player)
    opp_orbs = count_orbs(orbs, owners, GREEN if neuralforge_player==RED else RED)
    return w, MAX_TURNS, nf_orbs - opp_orbs

# ── Matchup runner ───────────────────────────────────────

def run_matchup(opponent_name, opponent_fn, games=GAMES_PER_MATCHUP):
    print(f"\n{'─'*52}")
    print(f"  NeuralForge  vs  {opponent_name}")
    print(f"{'─'*52}")

    results = {'wins': 0, 'losses': 0, 'ties': 0,
               'margins': [], 'turns': []}

    for side_name, nf_player in [('RED', RED), ('GREEN', GREEN)]:
        side_wins = 0
        print(f"\n  NeuralForge as {side_name} ({games} games):")
        for g in range(games):
            t0 = time.time()
            winner, turns, margin = play_game(nf_player, opponent_fn, opponent_name)
            elapsed = time.time() - t0

            if winner == nf_player:
                outcome = 'WIN  ✓'
                results['wins'] += 1
                side_wins += 1
            elif winner is None:
                outcome = 'TIE  ='
                results['ties'] += 1
            else:
                outcome = 'LOSS ✗'
                results['losses'] += 1

            results['margins'].append(margin)
            results['turns'].append(turns)
            print(f"    Game {g+1}: {outcome}  "
                  f"margin={margin:+d}  turn={turns}  ({elapsed:.1f}s)")

        print(f"  {side_name} record: {side_wins}/{games}")

    total   = results['wins'] + results['losses'] + results['ties']
    win_pct = int(results['wins'] / total * 100) if total > 0 else 0
    avg_margin = sum(results['margins']) / len(results['margins']) if results['margins'] else 0
    avg_turns  = sum(results['turns'])   / len(results['turns'])   if results['turns']   else 0

    print(f"\n  Summary vs {opponent_name}:")
    print(f"    Win rate   : {results['wins']}/{total}  ({win_pct}%)")
    print(f"    Avg margin : {avg_margin:+.1f} orbs")
    print(f"    Avg turns  : {avg_turns:.0f}")

    return win_pct, avg_margin

# ── Main ────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("  NeuralForge Tournament")
    print(f"  {GAMES_PER_MATCHUP*2} games per opponent  |  "
          f"Max {MAX_TURNS} turns  |  "
          f"Move budget {NEURALFORGE_TIME}s")
    print("=" * 52)

    # Patch time limit for this test run
    import NeuralForge_bot as nb
    nb.TIME_LIMIT = NEURALFORGE_TIME

    scoreboard = []

    # Matchup 1: vs Random
    def random_fn(orbs, owners, player, total_orbs):
        return random_move(owners, player)

    pct, margin = run_matchup("Random Bot", random_fn)
    scoreboard.append(("Random Bot",  pct, margin))

    # Matchup 2: vs Greedy
    def greedy_fn(orbs, owners, player, total_orbs):
        return greedy_bot.get_move(orbs, owners, player, total_orbs)

    pct, margin = run_matchup("Greedy Bot", greedy_fn)
    scoreboard.append(("Greedy Bot",  pct, margin))

    # Matchup 3: vs Minimax depth-2
    def minimax_fn(orbs, owners, player, total_orbs):
        return minimax_bot.get_move(orbs, owners, player, total_orbs)

    pct, margin = run_matchup("Minimax Bot (depth-2)", minimax_fn)
    scoreboard.append(("Minimax Bot", pct, margin))

    # ── Final scoreboard ────────────────────────────────
    print(f"\n{'='*52}")
    print("  FINAL SCOREBOARD")
    print(f"{'='*52}")
    print(f"  {'Opponent':<22} {'Win rate':>10} {'Avg margin':>12}")
    print(f"  {'─'*22} {'─'*10} {'─'*12}")
    for name, pct, margin in scoreboard:
        bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
        print(f"  {name:<22} {bar} {pct:>3}%  {margin:>+8.1f}")
    print(f"{'='*52}")

    overall = sum(p for _, p, _ in scoreboard) / len(scoreboard)
    print(f"  Overall average: {overall:.0f}%")
    if overall >= 85:
        print("  Verdict: DOMINANT — ready to win ✓")
    elif overall >= 70:
        print("  Verdict: STRONG — competitive, tune heuristic")
    else:
        print("  Verdict: NEEDS WORK — review losses carefully")
    print(f"{'='*52}")

if __name__ == "__main__":
    main()