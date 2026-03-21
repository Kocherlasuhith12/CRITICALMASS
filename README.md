# 💥 CRITICALMASS

<div align="center">

![Chain Reaction](https://img.shields.io/badge/Game-Chain%20Reaction-red?style=for-the-badge&logo=python&logoColor=white)
![Board](https://img.shields.io/badge/Board-12%20×%208-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Competition](https://img.shields.io/badge/NJACK-IIT%20Patna-darkblue?style=for-the-badge)
![Fest](https://img.shields.io/badge/Apeiron-2026-gold?style=for-the-badge)

**The ultimate test of algorithmic supremacy.**  
An AI bot engineered to play — and dominate — the game of Chain Reaction.

*Organized by NJACK, IIT Patna | Apeiron Fest*

</div>

---

## 🧠 What is CRITICALMASS?

**CRITICALMASS** is a competitive AI bot built for the *Chain Reaction* challenge — a turn-based strategy game where two players (Red vs Green) battle for total board control on a **12 × 8 grid**.

The goal isn't just to play. It's to **orchestrate total board annihilation**.

---

## 🎮 The Game: Chain Reaction

| Rule | Details |
|------|---------|
| **Board** | 12 × 8 grid |
| **Players** | 🔴 Red vs 🟢 Green |
| **Turn** | Players alternate placing orbs on the board |
| **Critical Mass** | Each cell has a limit based on its neighbors (corners = 2, edges = 3, center = 4) |
| **Explosion** | When a cell hits critical mass, it explodes — sending orbs to adjacent cells and claiming them |
| **Chain Reactions** | Explosions can trigger further explosions, creating cascading takeovers |
| **Win Condition** | Eliminate **all** of the opponent's orbs from the board |

> ⚡ The board is unpredictable. Chain reactions are exponential. One wrong move cascades. One smart move dominates.

---

## 📁 Project Structure

```
CRITICALMASS/
│
├── arena.py            # Game arena — simulates the board, handles turns & explosions
├── neuralforge_bot.py  # 🤖 Primary AI bot — the competitor
├── teamname_bot.py     # Named team bot entry
├── test_bot.py         # Testing & benchmarking bot logic
└── visualize.py        # Board visualizer — watch the bot play in real time
```

---

## 🤖 Bot Strategy

The bot implements a strategic decision-making engine that evaluates:

- **Threat detection** — identifying cells close to critical mass (opponent's and own)
- **Chain reaction simulation** — predicting explosion cascades before committing a move
- **Corner & edge prioritization** — low critical-mass cells that are harder to capture
- **Offensive vs. defensive balance** — knowing when to attack vs. fortify

> The bot doesn't just react to the board — it thinks several moves ahead.

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.10+
```

No external dependencies required for core bot logic.

### Clone the Repo

```bash
git clone https://github.com/Kocherlasuhith12/CRITICALMASS.git
cd CRITICALMASS
```

### Run a Bot Battle

```bash
python arena.py
```

### Watch the Bot Play (Visualizer)

```bash
python visualize.py
```

### Test Your Bot

```bash
python test_bot.py
```

---

## ⚙️ How the Arena Works

1. `arena.py` initializes a 12×8 board and manages game state
2. Each bot receives the current board state and must return a valid `(row, col)` move
3. The arena handles orb placement, explosion logic, and chain reactions
4. The game ends when one player has no orbs left on the board

**Bot interface:**
```python
def get_move(board, player):
    # board: 2D list representing current game state
    # player: 'R' (Red) or 'G' (Green)
    # return: (row, col) tuple for your move
    ...
    return (row, col)
```

---

## 🏆 Competition Details

| Detail | Info |
|--------|------|
| **Competition** | CRITICAL MASS – AI Bot Competition |
| **Organizer** | NJACK, IIT Patna |
| **Fest** | Apeiron |
| **Format** | Head-to-head bot battles |
| **Language** | Python |

---

## 👨‍💻 Author

**KKS Suhith Sravan Babu**  
B.Tech CSE | SRM Institute of Science and Technology, Trichy  
[GitHub](https://github.com/Kocherlasuhith12)

---

<div align="center">

*"Don't just play the game. Orchestrate total board annihilation."*

</div>
