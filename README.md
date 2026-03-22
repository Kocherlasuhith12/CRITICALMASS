# 💥 CRITICALMASS

<div align="center">

![Game](https://img.shields.io/badge/🎮_GAME-Chain_Reaction-black?style=for-the-badge)
![Board](https://img.shields.io/badge/BOARD-12_×_8-1e3a8a?style=for-the-badge)
![Python](https://img.shields.io/badge/PYTHON-3.10+-2563eb?style=for-the-badge&logo=python&logoColor=white)
![NJACK](https://img.shields.io/badge/NJACK-IIT_Patna-7c3aed?style=for-the-badge)
![Apeiron](https://img.shields.io/badge/APEIRON-2026-059669?style=for-the-badge)

<br/>

> **An Alpha-Beta Minimax AI bot engineered to dominate Chain Reaction.**
> Built for the Critical Mass competition organized by NJACK, IIT Patna — Apeiron Fest 2026.

<br/>

| Metric | Result |
|--------|--------|
| vs Random Bot | **100% win rate** |
| vs Greedy Bot | **100% win rate** |
| vs Minimax Bot (depth-2) | **100% win rate** |
| Unit Tests | **37 / 37 passing** |
| Move Timing | **< 1.0s guaranteed** |
| Competition Interface | **`get_move(state, player_id)` ✓** |

</div>

---

## 🧠 Strategy Overview

NeuralForge Bot uses **Iterative Deepening Alpha-Beta Minimax** — the same class of algorithm used in world-class chess engines. It doesn't follow hardcoded rules. It *thinks*.

```
Every move:
  1. Check opening book  →  instant corner claim (0ms)
  2. Detect threats      →  scan for imminent enemy explosions
  3. Check capture mode  →  if winning clearly, go for the kill
  4. Alpha-Beta search   →  iterative deepening until 0.85s budget
  5. Return best move    →  always within 1.0s
```

---

## ⚙️ Architecture

### 1. Opening Book
The first 4 moves are hardcoded to the 4 corners. Corners have **critical mass 2** — they explode with just 2 orbs, faster than any other cell. No search time wasted on moves that are trivially optimal.

```python
OPENING_BOOK = {
    RED:   [(0,0), (7,11), (0,11), (7,0)],
    GREEN: [(7,11), (0,0), (7,0), (0,11)],
}
```

### 2. Chain Explosion Engine
Iterative BFS — no recursion, no stack overflow risk. Every chain reaction resolves correctly regardless of length.

```python
def apply_move(orbs, owners, row, col, player):
    # Place orb → trigger BFS explosion queue
    # Captures all reachable enemy cells via chain
    # Returns new (orbs, owners) — original untouched
```

### 3. Alpha-Beta Minimax
Searches the game tree with full Alpha-Beta pruning. Beta cutoffs eliminate branches the opponent would never allow — halving the effective branching factor and doubling search depth.

```
Without pruning:  O(b^d)      → depth 3 at ~90 moves = 729,000 nodes
With Alpha-Beta:  O(b^(d/2))  → depth 6 at same budget
```

### 4. Iterative Deepening
Searches depth 1 → 2 → 3 → ... until the 0.85s time budget expires. Always returns the best answer from the deepest **complete** search. Never exceeds 1.0s.

### 5. Heuristic Evaluation (v3)

Phase-aware scoring that adapts across the game:

| Factor | Formula | Purpose |
|--------|---------|---------|
| Orb count | `n × 1.0` | Raw material |
| Instability | `(n/CM) × 4.0` | Near-critical cells are powerful |
| Positional value | `(4-CM) × 3` | Corners > edges > inner |
| Chain potential | `+2 per near-critical ally` | Cascade readiness |
| Danger exposure | `-3 per near-critical enemy` | Threat awareness |

| Phase | Condition | Weight emphasis |
|-------|-----------|-----------------|
| Opening | `move_count < 12` | Territory + cell ownership |
| Midgame | `12 ≤ moves, orbs ≤ 55` | Balance all factors |
| Endgame | `total orbs > 55` | Aggressive orb maximisation |

### 6. Threat Detection
Before every move, scans the entire board for enemy cells at critical mass. Flags our cells under immediate threat and prioritises defensive responses.

### 7. Capture Mode
When the bot has 40%+ more orbs than the opponent, it switches to pure elimination — only considering moves that directly attack enemy cells.

### 8. Critical Moment Depth Boost
When the opponent has 2+ imminent explosions or either player is near-eliminated, the time budget extends to 0.92s. Thinks harder in the moments that matter most.

### 9. Move Ordering (v3)
Moves sorted before search so best candidates are tried first — maximising Alpha-Beta cutoffs:

```
+20  cell one orb from exploding
+10  cell two orbs from exploding
+8   adjacent to enemy near-critical (attack timing)
+6   adjacent to friendly near-critical (chain setup)
+5   adjacent to any enemy cell
+(4-CM)×3  corner/edge positional bonus
```

---

## 📁 Project Structure

```
CriticalMass/
│
├── NeuralForge_bot.py    # 🤖 Submit this — competition entry
├── neuralforge_bot.py    # 🔧 Local development copy
│
├── greedy_bot.py         # 🎯 Test opponent: greedy (no lookahead)
├── minimax_bot.py        # 🔍 Test opponent: Minimax depth-2
├── tournament.py         # 🏆 Full tournament vs all opponents
│
├── arena.py              # ⚔️  Quick bot vs random games
├── test_bot.py           # ✅  37-test unit suite
├── visualize.py          # 👁️  Live board viewer in terminal
└── README.md
```

---

## 🚀 Quick Start

```bash
# Install dependency
pip install numpy

# Run full test suite (37 tests)
python3 test_bot.py

# Tournament: NeuralForge vs Greedy vs Minimax vs Random
python3 tournament.py

# Watch the bot play live in terminal
python3 visualize.py
```

---

## 🏆 Tournament Results

```
════════════════════════════════════════════════════
  FINAL SCOREBOARD
════════════════════════════════════════════════════
  Opponent           Win rate             Avg margin
  ───────────────── ──────────────────── ───────────
  Random Bot         ██████████  100%      +69.6 orbs
  Greedy Bot         ██████████  100%      +25.5 orbs
  Minimax (depth-2)  ██████████  100%      +25.5 orbs
════════════════════════════════════════════════════
  Overall: 30/30     Verdict: DOMINANT ✓
════════════════════════════════════════════════════
```

Against Greedy and Minimax bots, the game ends at **turn 26** — the bot eliminates both before they reach midgame.

---

## 🔌 Competition Interface

The bot implements the **official competition function signature**:

```python
def get_move(state, player_id):
    """
    state     : 12x8 board — list of lists of (owner_id, orb_count) tuples
                Empty cell = (None, 0)
    player_id : 0 = Red (first player), 1 = Green (second player)
    Returns   : (row, col) tuple
    """
```

---

## 📋 Submission Details

| Item | Detail |
|------|--------|
| Competition | Critical Mass — The Ultimate AI Bot-Making Competition |
| Organiser | NJACK, IIT Patna — Apeiron Fest 2026 |
| Submission file | `NeuralForge_bot.py` |
| Strategy document | `NeuralForge_Strategy.pdf` |
| Deadline | 28 March 2026, 12:00 PM IST |
| Submit via | Google Form (registration link) |
| Allowed libraries | NumPy (used), Pandas, PyTorch, TensorFlow |
| Threads | None — fully compliant |

---

## 🔧 Technical Specs

| Spec | Detail |
|------|--------|
| Language | Python 3.11 |
| Board representation | Two `8×12` NumPy `int32` arrays |
| Explosion engine | Iterative BFS — no recursion |
| Search algorithm | Iterative deepening Alpha-Beta, depths 1–12 |
| Time management | `_Timeout` exception at 0.85s, best answer returned |
| Precomputation | Critical mass map + neighbour list at import time |
| Unit tests | 37 tests — board, explosion, chains, timing, interface |

---

## 👤 Author

**Kocherla Koteswara Suhith Sravan Babu**
B.Tech CSE — SRM Institute of Science and Technology, Trichy

[![GitHub](https://img.shields.io/badge/GitHub-Kocherlasuhith12-black?style=flat&logo=github)](https://github.com/Kocherlasuhith12)
