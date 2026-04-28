# Tic-Tac-Toe — An Adversarial-Search Project

A Pygame implementation of Tic-Tac-Toe used as a testbed for classical AI
search techniques. Built for **CPSC 481 — Artificial Intelligence** (Track A: Game / Puzzle Intelligence).

This project compares three approaches on the same game:

| Mode | Algorithm | Notes |
| ---- | --------- | ----- |
| Easy | Heuristic evaluation | win → center → corner → edge |
| Hard | Minimax | Full game-tree search |
| Hard (optimized) | Minimax + α-β pruning | Same play, fewer nodes expanded |

You can play against either AI, or run agent-vs-agent simulations and compare
win rates and compute time per side.

---

## Requirements

- Python **3.9+**
- [pygame](https://www.pygame.org/) `2.6.1`


## Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd 481-Final-Project

# 2. (Recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (PowerShell)

# 3. Install dependencies
pip install -r requirements.txt
```

## Run

```bash
python3 tic_tac_toe.py
```

A 600 × 700 window opens with the home screen. Click a mode to begin.

## Modes

**I. Easy Mode** — You play X against a heuristic agent (O). Good for warm-up
games; the AI can be beaten.

**II. Hard Mode** — You play X against minimax with α-β pruning (O). The agent
plays optimally. The best you can do is draw.

**III. Agent vs Agent** — Pick a matchup and the program simulates *N* games,
then reports wins, draws, and total compute time per side. Available
matchups:

- Easy vs Easy
- Hard vs Hard (Minimax)
- Hard vs Hard (Alpha-Beta)
- Easy (X) vs Hard (O)
- Hard (X) vs Easy (O)

> **Note.** The agents are deterministic, so the same matchup currently
> replays the same game *N* times. To get varied results / meaningful win
> distributions, randomize tie-breaking among equal-value moves (or randomize
> the opening move).

## Project Structure

```
481-Final-Project/
├── tic_tac_toe.py      # Main program (UI + AI)
├── requirements.txt    # Python dependencies
├── README.md
└── .gitignore
```

## Controls

- **Mouse** — click to place a mark or select a menu option
- **R** — restart current game (after game ends)
- **← MENU button** — return to home screen

## Authors

Kush Bajaria | AP Calderon |
California State University, Fullerton | CPSC 481, 2026
