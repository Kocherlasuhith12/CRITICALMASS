"""
test_bot.py — Full unit test suite for NeuralForge Bot
Usage: python3 test_bot.py
All tests should pass before submitting.
"""

from NeuralForge_bot import *
import time
 
PASS = "✓"
FAIL = "✗"
errors = 0

def check(condition, label, got=None, expected=None):
    global errors
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}  →  got={got}, expected={expected}")
        errors += 1

print("=" * 50)
print("  NeuralForge Bot — Test Suite")
print("=" * 50)

# ── Test 1: Board constants ──────────────────────────────
print("\n[1] Board Constants")
check(ROWS == 8,                         "ROWS = 8")
check(COLS == 12,                        "COLS = 12")
check(CRITICAL_MASS[0][0]  == 2,        "Corner  (0,0)  CM = 2")
check(CRITICAL_MASS[0][11] == 2,        "Corner  (0,11) CM = 2")
check(CRITICAL_MASS[7][0]  == 2,        "Corner  (7,0)  CM = 2")
check(CRITICAL_MASS[7][11] == 2,        "Corner  (7,11) CM = 2")
check(CRITICAL_MASS[0][5]  == 3,        "Edge    (0,5)  CM = 3")
check(CRITICAL_MASS[3][0]  == 3,        "Edge    (3,0)  CM = 3")
check(CRITICAL_MASS[3][5]  == 4,        "Inner   (3,5)  CM = 4")
check(len(NEIGHBORS[(0,0)]) == 2,       "Corner  (0,0)  neighbours = 2")
check(len(NEIGHBORS[(0,5)]) == 3,       "Edge    (0,5)  neighbours = 3")
check(len(NEIGHBORS[(3,5)]) == 4,       "Inner   (3,5)  neighbours = 4")

# ── Test 2: make_state ───────────────────────────────────
print("\n[2] make_state()")
o, ow = make_state()
check(o.shape  == (8, 12), "orbs shape  = (8, 12)")
check(ow.shape == (8, 12), "owners shape= (8, 12)")
check(o.sum()  == 0,       "orbs all zero")
check(ow.sum() == 0,       "owners all zero")

# ── Test 3: apply_move basic ─────────────────────────────
print("\n[3] apply_move() — basic placement")
o, ow = make_state()
o2, ow2 = apply_move(o, ow, 3, 5, RED)
check(o2[3][5]  == 1,   "orbs[3][5] = 1 after placing")
check(ow2[3][5] == RED, "owners[3][5] = RED after placing")
check(o[3][5]   == 0,   "original orbs unchanged (immutable)")

# ── Test 4: Corner explosion ─────────────────────────────
print("\n[4] apply_move() — corner explosion")
o, ow = make_state()
o[0][0] = 1; ow[0][0] = RED
o2, ow2 = apply_move(o, ow, 0, 0, RED)  # 2nd orb → CM=2 → explodes
check(o2[0][0]  == 0,   "Corner (0,0) emptied after explosion")
check(o2[0][1]  == 1,   "Right  (0,1) received 1 orb")
check(o2[1][0]  == 1,   "Below  (1,0) received 1 orb")
check(ow2[0][1] == RED, "Right  (0,1) owned by RED")
check(ow2[1][0] == RED, "Below  (1,0) owned by RED")

# ── Test 5: Chain reaction ───────────────────────────────
print("\n[5] apply_move() — chain reaction")
o, ow = make_state()
o[0][0]  = 1; ow[0][0]  = RED    # corner with 1 orb
o[0][1]  = 2; ow[0][1]  = GREEN  # edge with 2 orbs (needs 1 more to explode)
o2, ow2 = apply_move(o, ow, 0, 0, RED)
# RED at (0,0): now 2 orbs = CM → explodes → sends to (0,1) and (1,0)
# (0,1): now 3 orbs = CM → explodes → enemy captured
check(ow2[0][1] != GREEN, "Enemy cell (0,1) captured after chain")
check(not bool(np.any((ow2 == GREEN) & (o2 > 0))), "All GREEN orbs eliminated")

# ── Test 6: Capture enemy cell ───────────────────────────
print("\n[6] apply_move() — enemy capture")
o, ow = make_state()
o[0][1] = 2; ow[0][1] = GREEN
o[0][0] = 1; ow[0][0] = RED
o2, ow2 = apply_move(o, ow, 0, 0, RED)
check(ow2[0][1] != GREEN, "GREEN cell captured by RED chain")

# ── Test 7: Valid moves ──────────────────────────────────
print("\n[7] get_valid_moves()")
_, ow = make_state()
vm = get_valid_moves(ow, RED)
check(len(vm) == 96, f"Empty board: 96 valid moves", len(vm), 96)

# With some owned cells
o, ow = make_state()
o[0][0] = 1; ow[0][0] = RED
o[0][1] = 1; ow[0][1] = GREEN
vm_red   = get_valid_moves(ow, RED)
vm_green = get_valid_moves(ow, GREEN)
check((0,0) in vm_red,       "RED can play on own cell (0,0)")
check((0,1) not in vm_red,   "RED cannot play on GREEN cell (0,1)")
check((0,1) in vm_green,     "GREEN can play on own cell (0,1)")
check((0,0) not in vm_green, "GREEN cannot play on RED cell (0,0)")

# ── Test 8: Winner detection ─────────────────────────────
print("\n[8] get_winner()")
o, ow = make_state()
o[0][0] = 1; ow[0][0] = GREEN
check(get_winner(o, ow, 2)  is None,  "total_orbs=2 → no winner (too early)")
check(get_winner(o, ow, 10) == GREEN, "Only GREEN orbs → GREEN wins")
o2, ow2 = make_state()
o2[3][5] = 2; ow2[3][5] = RED
check(get_winner(o2, ow2, 10) == RED, "Only RED orbs → RED wins")
o3, ow3 = make_state()
o3[0][0] = 1; ow3[0][0] = RED
o3[7][11] = 1; ow3[7][11] = GREEN
check(get_winner(o3, ow3, 10) is None, "Both players have orbs → no winner")

# ── Test 9: Move timing ──────────────────────────────────
print("\n[9] Timing — every move must be < 1.0 second")
o, ow = make_state()
all_ok = True
worst  = 0.0
for i in range(3):
    t0 = time.time()
    mv = get_best_move(o, ow, RED, 0)
    elapsed = time.time() - t0
    worst = max(worst, elapsed)
    if elapsed >= 1.0:
        all_ok = False
    print(f"    Call {i+1}: {elapsed:.3f}s  move={mv}")
check(all_ok, f"All moves under 1.0s (worst={worst:.3f}s)")

# ── Test 10: get_move interface (official competition format) ──
print("\n[10] get_move() — competition interface")
# Official format: 2D list of (owner_id, orb_count) tuples
# Empty cell = (None, 0), player_id = 0 or 1
state_empty = [[(None, 0)] * COLS for _ in range(ROWS)]
mv = get_move(state_empty, 0)
check(isinstance(mv, tuple),  "Returns a tuple")
check(len(mv) == 2,           "Tuple has 2 elements")
check(0 <= mv[0] < ROWS,     f"Row {mv[0]} in range [0,{ROWS})")
check(0 <= mv[1] < COLS,     f"Col {mv[1]} in range [0,{COLS})")
mv2 = get_move(state_empty, 1)
check(isinstance(mv2, tuple), "player_id=1 returns valid move")
state_mid = [[(None, 0)] * COLS for _ in range(ROWS)]
state_mid[0][0]  = (0, 1)
state_mid[7][11] = (1, 1)
mv3 = get_move(state_mid, 0)
check(isinstance(mv3, tuple), "Mid-game state returns valid move")

# ── Summary ──────────────────────────────────────────────
print()
print("=" * 50)
if errors == 0:
    print("  ALL TESTS PASSED ✓")
    print("  Bot is bug-free and ready to compete!")
else:
    print(f"  {errors} TEST(S) FAILED ✗")
    print("  Fix the issues above before submitting.")
print("=" * 50)
