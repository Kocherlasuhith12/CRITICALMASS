"""
arena.py — Bot vs Random (fast version)
Caps at 80 turns — winner decided by orb count if no elimination
Usage: python3 arena.py
"""

from NeuralForge_bot import (
    ROWS, COLS, RED, GREEN, EMPTY,
    make_state, apply_move, get_winner, get_valid_moves,
    get_best_move, count_orbs
)
import numpy as np
import random, time

MAX_TURNS = 80

def random_move(owners, player):
    moves = get_valid_moves(owners, player)
    return random.choice(moves) if moves else None

def play_one_game(bot_player, game_num):
    orbs, owners = make_state()
    current = RED

    for turn in range(MAX_TURNS):
        total_orbs = int(np.sum(orbs))

        w = get_winner(orbs, owners, total_orbs)
        if w:
            label = "WIN  ✓" if w == bot_player else "LOSS ✗"
            print(f"  Game {game_num}: {label}  eliminated at turn {turn}")
            return w

        if current == bot_player:
            mv = get_best_move(orbs, owners, current, total_orbs)
        else:
            mv = random_move(owners, current)

        if mv is None:
            break
        orbs, owners = apply_move(orbs, owners, mv[0], mv[1], current)
        current = GREEN if current == RED else RED

    # No elimination — judge by orb count
    bot_orbs = count_orbs(orbs, owners, bot_player)
    opp      = GREEN if bot_player == RED else RED
    opp_orbs = count_orbs(orbs, owners, opp)
    won      = bot_orbs > opp_orbs
    print(f"  Game {game_num}: {'WIN  ✓' if won else 'LOSS ✗'}  "
          f"(orbs: bot={bot_orbs} vs random={opp_orbs} at turn {MAX_TURNS})")
    return bot_player if won else opp

def run(games=5):
    print("=" * 52)
    print("  NeuralForge Bot v4 vs Random")
    print(f"  Max turns: {MAX_TURNS}")
    print("=" * 52)

    print(f"\nBot as RED — {games} games:")
    t0   = time.time()
    wins = sum(1 for i in range(games)
               if play_one_game(RED, i+1) == RED)
    print(f"  Result: {wins}/{games}  ({time.time()-t0:.1f}s)\n")

    print(f"Bot as GREEN — {games} games:")
    t0    = time.time()
    wins2 = sum(1 for i in range(games)
                if play_one_game(GREEN, i+1) == GREEN)
    print(f"  Result: {wins2}/{games}  ({time.time()-t0:.1f}s)\n")

    total = wins + wins2
    print("=" * 52)
    print(f"  Total: {total}/{games*2}  ({int(total/(games*2)*100)}% win rate)")
    if total >= games + 2:
        print("  STRONG ✓ — bot is dominating random play")
    else:
        print("  Needs tuning")
    print("=" * 52)

if __name__ == "__main__":
    run(games=5)