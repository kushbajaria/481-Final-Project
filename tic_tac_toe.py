"""
Tic Tac Toe with Pygame — 3 AI Difficulty Levels

Easy:   Random moves with basic heuristics (blocks obvious wins ~50% of the time)
Medium: Minimax with depth-limited search (depth 3) + heuristic evaluation
Hard:   Full Minimax with Alpha-Beta pruning (unbeatable)

Player = X (goes first), AI = O
"""

import sys
import random
import math
import pygame

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 600, 700  # extra 100px at top for status bar
BOARD_SIZE = 600
CELL = BOARD_SIZE // 3
LINE_W = 12
CIRCLE_R = CELL // 3
CIRCLE_W = 12
CROSS_W = 16
CROSS_PAD = CELL // 5
TOP_OFFSET = 100  # status bar height

# Colours
BG_COLOR      = (28, 28, 30)
LINE_COLOR    = (60, 60, 67)
CIRCLE_COLOR  = (10, 132, 255)   # blue
CROSS_COLOR   = (255, 69, 58)    # red
TEXT_COLOR     = (235, 235, 245)
BTN_COLOR     = (44, 44, 46)
BTN_HOVER     = (58, 58, 60)
WIN_LINE_COLOR= (48, 209, 88)    # green

# Board state tokens
EMPTY, PLAYER_X, PLAYER_O = 0, 1, 2

# ---------------------------------------------------------------------------
# Game logic helpers
# ---------------------------------------------------------------------------

def initial_board():
    return [[EMPTY] * 3 for _ in range(3)]


def available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]


def check_winner(board):
    """Return (winner, winning_cells) or (None, None)."""
    lines = []
    for r in range(3):
        lines.append([(r, 0), (r, 1), (r, 2)])
    for c in range(3):
        lines.append([(0, c), (1, c), (2, c)])
    lines.append([(0, 0), (1, 1), (2, 2)])
    lines.append([(0, 2), (1, 1), (2, 0)])

    for cells in lines:
        vals = [board[r][c] for r, c in cells]
        if vals[0] != EMPTY and vals[0] == vals[1] == vals[2]:
            return vals[0], cells
    return None, None


def is_full(board):
    return all(board[r][c] != EMPTY for r in range(3) for c in range(3))


# ---------------------------------------------------------------------------
# AI: Easy — random with occasional block
# ---------------------------------------------------------------------------

def ai_easy(board):
    """Mostly random. 50 % chance to block an immediate player win."""
    moves = available_moves(board)
    if not moves:
        return None

    # 50 % chance: try to block player winning move
    if random.random() < 0.5:
        for r, c in moves:
            board[r][c] = PLAYER_X
            w, _ = check_winner(board)
            board[r][c] = EMPTY
            if w == PLAYER_X:
                return (r, c)

    return random.choice(moves)


# ---------------------------------------------------------------------------
# AI: Medium — depth-limited minimax with heuristic evaluation
# ---------------------------------------------------------------------------

def heuristic_eval(board):
    """Score the board from O's perspective using a simple heuristic."""
    score = 0
    lines = []
    for r in range(3):
        lines.append([board[r][0], board[r][1], board[r][2]])
    for c in range(3):
        lines.append([board[0][c], board[1][c], board[2][c]])
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        o_count = line.count(PLAYER_O)
        x_count = line.count(PLAYER_X)
        if o_count > 0 and x_count == 0:
            score += 10 ** o_count
        elif x_count > 0 and o_count == 0:
            score -= 10 ** x_count
    return score


def minimax_limited(board, depth, is_maximizing, max_depth):
    """Minimax with depth limit and heuristic fallback."""
    winner, _ = check_winner(board)
    if winner == PLAYER_O:
        return 1000
    if winner == PLAYER_X:
        return -1000
    if is_full(board):
        return 0
    if depth >= max_depth:
        return heuristic_eval(board)

    moves = available_moves(board)
    if is_maximizing:
        best = -math.inf
        for r, c in moves:
            board[r][c] = PLAYER_O
            best = max(best, minimax_limited(board, depth + 1, False, max_depth))
            board[r][c] = EMPTY
        return best
    else:
        best = math.inf
        for r, c in moves:
            board[r][c] = PLAYER_X
            best = min(best, minimax_limited(board, depth + 1, True, max_depth))
            board[r][c] = EMPTY
        return best


def ai_medium(board):
    """Depth-limited minimax (depth 3) — makes decent moves but beatable."""
    moves = available_moves(board)
    if not moves:
        return None
    best_score = -math.inf
    best_move = moves[0]
    random.shuffle(moves)  # tie-break randomly
    for r, c in moves:
        board[r][c] = PLAYER_O
        score = minimax_limited(board, 0, False, 3)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


# ---------------------------------------------------------------------------
# AI: Hard — full minimax with alpha-beta pruning (unbeatable)
# ---------------------------------------------------------------------------

def minimax_ab(board, is_maximizing, alpha, beta):
    """Full-depth minimax with alpha-beta pruning."""
    winner, _ = check_winner(board)
    if winner == PLAYER_O:
        return 10
    if winner == PLAYER_X:
        return -10
    if is_full(board):
        return 0

    if is_maximizing:
        best = -math.inf
        for r, c in available_moves(board):
            board[r][c] = PLAYER_O
            best = max(best, minimax_ab(board, False, alpha, beta))
            board[r][c] = EMPTY
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for r, c in available_moves(board):
            board[r][c] = PLAYER_X
            best = min(best, minimax_ab(board, True, alpha, beta))
            board[r][c] = EMPTY
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def ai_hard(board):
    """Unbeatable AI using full minimax + alpha-beta pruning."""
    moves = available_moves(board)
    if not moves:
        return None
    best_score = -math.inf
    best_move = moves[0]
    for r, c in moves:
        board[r][c] = PLAYER_O
        score = minimax_ab(board, False, -math.inf, math.inf)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move


AI_FUNCS = {
    "Easy": ai_easy,
    "Medium": ai_medium,
    "Hard": ai_hard,
}

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_board(screen):
    for i in range(1, 3):
        # Vertical
        pygame.draw.line(screen, LINE_COLOR,
                         (i * CELL, TOP_OFFSET), (i * CELL, TOP_OFFSET + BOARD_SIZE), LINE_W)
        # Horizontal
        pygame.draw.line(screen, LINE_COLOR,
                         (0, TOP_OFFSET + i * CELL), (WIDTH, TOP_OFFSET + i * CELL), LINE_W)


def draw_pieces(screen, board):
    for r in range(3):
        for c in range(3):
            cx = c * CELL + CELL // 2
            cy = TOP_OFFSET + r * CELL + CELL // 2
            if board[r][c] == PLAYER_O:
                pygame.draw.circle(screen, CIRCLE_COLOR, (cx, cy), CIRCLE_R, CIRCLE_W)
            elif board[r][c] == PLAYER_X:
                offset = CELL // 2 - CROSS_PAD
                pygame.draw.line(screen, CROSS_COLOR,
                                 (cx - offset, cy - offset), (cx + offset, cy + offset), CROSS_W)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (cx + offset, cy - offset), (cx - offset, cy + offset), CROSS_W)


def draw_winning_line(screen, cells):
    r1, c1 = cells[0]
    r2, c2 = cells[2]
    start = (c1 * CELL + CELL // 2, TOP_OFFSET + r1 * CELL + CELL // 2)
    end   = (c2 * CELL + CELL // 2, TOP_OFFSET + r2 * CELL + CELL // 2)
    pygame.draw.line(screen, WIN_LINE_COLOR, start, end, LINE_W + 4)


# ---------------------------------------------------------------------------
# Button helper
# ---------------------------------------------------------------------------

class Button:
    def __init__(self, rect, text, font, color=BTN_COLOR, hover=BTN_HOVER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover = hover

    def draw(self, screen, mouse_pos):
        c = self.hover if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=10)
        surf = self.font.render(self.text, True, TEXT_COLOR)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tic Tac Toe — AI Difficulty Levels")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("Helvetica", 42, bold=True)
    font_med   = pygame.font.SysFont("Helvetica", 28)
    font_small = pygame.font.SysFont("Helvetica", 22)

    # ---- State ----
    STATE_MENU = 0
    STATE_PLAY = 1
    STATE_OVER = 2

    state = STATE_MENU
    difficulty = "Easy"
    board = initial_board()
    turn = PLAYER_X  # player always starts
    winner = None
    win_cells = None
    status_text = ""

    # ---- Menu buttons ----
    btn_w, btn_h = 160, 50
    gap = 30
    total = 3 * btn_w + 2 * gap
    sx = (WIDTH - total) // 2
    sy = 350

    btn_easy   = Button((sx, sy, btn_w, btn_h), "Easy", font_med)
    btn_medium = Button((sx + btn_w + gap, sy, btn_w, btn_h), "Medium", font_med)
    btn_hard   = Button((sx + 2 * (btn_w + gap), sy, btn_w, btn_h), "Hard", font_med)
    menu_buttons = [btn_easy, btn_medium, btn_hard]

    # Restart / Menu buttons (game over)
    btn_restart = Button((WIDTH // 2 - 170, HEIGHT - 65, 160, 45), "Restart", font_med)
    btn_menu    = Button((WIDTH // 2 + 10, HEIGHT - 65, 160, 45), "Menu", font_med)

    def reset_game(diff):
        nonlocal board, turn, winner, win_cells, state, difficulty, status_text
        difficulty = diff
        board = initial_board()
        turn = PLAYER_X
        winner = None
        win_cells = None
        state = STATE_PLAY
        status_text = "Your turn (X)"

    def do_ai_move():
        nonlocal turn, winner, win_cells, state, status_text
        move = AI_FUNCS[difficulty](board)
        if move:
            board[move[0]][move[1]] = PLAYER_O
            winner, win_cells = check_winner(board)
            if winner:
                status_text = "AI wins!"
                state = STATE_OVER
            elif is_full(board):
                status_text = "Draw!"
                state = STATE_OVER
            else:
                turn = PLAYER_X
                status_text = "Your turn (X)"

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ---- Menu ----
                if state == STATE_MENU:
                    for btn, diff in zip(menu_buttons, ["Easy", "Medium", "Hard"]):
                        if btn.clicked(event.pos):
                            reset_game(diff)

                # ---- Playing ----
                elif state == STATE_PLAY and turn == PLAYER_X:
                    x, y = event.pos
                    if y > TOP_OFFSET:
                        c = x // CELL
                        r = (y - TOP_OFFSET) // CELL
                        if 0 <= r < 3 and 0 <= c < 3 and board[r][c] == EMPTY:
                            board[r][c] = PLAYER_X
                            winner, win_cells = check_winner(board)
                            if winner:
                                status_text = "You win!"
                                state = STATE_OVER
                            elif is_full(board):
                                status_text = "Draw!"
                                state = STATE_OVER
                            else:
                                turn = PLAYER_O
                                status_text = "AI thinking..."

                # ---- Game Over ----
                elif state == STATE_OVER:
                    if btn_restart.clicked(event.pos):
                        reset_game(difficulty)
                    elif btn_menu.clicked(event.pos):
                        state = STATE_MENU

        # AI move (outside event loop so it happens on next frame)
        if state == STATE_PLAY and turn == PLAYER_O:
            do_ai_move()

        # ---- Draw ----
        screen.fill(BG_COLOR)

        if state == STATE_MENU:
            # Title
            title = font_large.render("Tic Tac Toe", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 160)))
            sub = font_med.render("Choose difficulty:", True, TEXT_COLOR)
            screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 280)))

            # Descriptions
            descs = [
                "Random + basic blocking",
                "Depth-limited minimax",
                "Full minimax + α-β pruning",
            ]
            for i, (btn, desc) in enumerate(zip(menu_buttons, descs)):
                btn.draw(screen, mouse_pos)
                d = font_small.render(desc, True, (142, 142, 147))
                screen.blit(d, d.get_rect(center=(btn.rect.centerx, sy + btn_h + 22)))

        else:
            # Status bar
            stat = font_med.render(status_text, True, TEXT_COLOR)
            screen.blit(stat, stat.get_rect(center=(WIDTH // 2, TOP_OFFSET // 2 - 5)))
            diff_label = font_small.render(f"Difficulty: {difficulty}", True, (142, 142, 147))
            screen.blit(diff_label, diff_label.get_rect(center=(WIDTH // 2, TOP_OFFSET // 2 + 25)))

            draw_board(screen)
            draw_pieces(screen, board)

            if win_cells:
                draw_winning_line(screen, win_cells)

            if state == STATE_OVER:
                btn_restart.draw(screen, mouse_pos)
                btn_menu.draw(screen, mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
