"""
visualize.py — Watch the bot play live in your terminal
Usage: python3 visualize.py
"""

from NeuralForge_bot import *
import random, os, time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(orbs, owners, turn):
    clear()
    print("╔══════════════════════════════════════════════════╗")
    print("║   NeuralForge Bot — Chain Reaction Live View     ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Turn: {turn:<5}   R = RED (bot)   G = GREEN (random) ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # Column headers
    print("     " + " ".join(f"{c:3}" for c in range(COLS)))
    print("     " + "───" * COLS)

    for r in range(ROWS):
        row_str = f"  {r} │"
        for c in range(COLS):
            n = int(orbs[r][c])
            o = int(owners[r][c])
            if n == 0:
                row_str += "  . "
            elif o == RED:
                row_str += f" R{n} "
            else:
                row_str += f" G{n} "
        print(row_str)

    print()
    r_total = int(sum(orbs[r][c] for r in range(ROWS)
                      for c in range(COLS) if owners[r][c] == RED))
    g_total = int(sum(orbs[r][c] for r in range(ROWS)
                      for c in range(COLS) if owners[r][c] == GREEN))

    bar_total = max(r_total + g_total, 1)
    r_bar = int((r_total / bar_total) * 30)
    g_bar = 30 - r_bar

    print(f"  RED  (bot)   : {'█' * r_bar}{'░' * g_bar} {r_total} orbs")
    print(f"  GREEN (rand) : {'░' * r_bar}{'█' * g_bar} {g_total} orbs")
    print()

def main():
    orbs, owners = make_state()
    current      = RED

    for turn in range(400):
        print_board(orbs, owners, turn)
        time.sleep(0.35)

        winner = get_winner(orbs, owners, turn)
        if winner:
            print_board(orbs, owners, turn)
            if winner == RED:
                print("  🏆  BOT (RED) WINS!")
            else:
                print("  💀  RANDOM (GREEN) WINS!")
            break

        if current == RED:
            mv = get_best_move(orbs, owners, current, turn)
        else:
            moves = get_valid_moves(owners, current)
            mv    = random.choice(moves) if moves else None

        if mv is None:
            break

        orbs, owners = apply_move(orbs, owners, mv[0], mv[1], current)
        current = GREEN if current == RED else RED

if __name__ == "__main__":
    main()