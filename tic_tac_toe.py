import pygame
import sys
import math
import time
import copy

pygame.init()

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 700
BOARD_TOP    = 120
CELL         = 160
LINE_W       = 5
CIRCLE_R     = 55
CIRCLE_W     = 12
CROSS_W      = 15
CROSS_OFF    = 40

BG           = (15,  15,  20)
GRID_COL     = (50,  50,  65)
X_COL        = (255, 100,  80)
O_COL        = ( 80, 180, 255)
BTN_MAIN     = (30,  30,  45)
BTN_HOVER    = (50,  50,  75)
BTN_BORDER   = (80,  80, 110)
EASY_COL     = ( 80, 200, 120)
HARD_COL     = (255, 100,  80)
AIVA_COL     = (180, 130, 255)
WHITE        = (240, 240, 245)
GRAY         = (120, 120, 140)
OVERLAY      = (10,  10,  15, 200)
RESULT_BG    = (20,  20,  30)

TITLE_FONT   = pygame.font.SysFont("Georgia",        52, bold=True)
LABEL_FONT   = pygame.font.SysFont("Courier New",    20, bold=True)
BTN_FONT     = pygame.font.SysFont("Courier New",    18, bold=True)
STATUS_FONT  = pygame.font.SysFont("Georgia",        26, bold=True)
SMALL_FONT   = pygame.font.SysFont("Courier New",    14)
TIMER_FONT   = pygame.font.SysFont("Courier New",    16, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe  —  AI")
clock  = pygame.time.Clock()

# ─── GAME STATE REPRESENTATION ────────────────────────────────────────────────
# Board is a list of 9 cells: 'X', 'O', or None
WINS = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # columns
    (0,4,8),(2,4,6)            # diagonals
]

def empty_board():
    return [None]*9

def check_winner(board):
    """Return 'X', 'O', or None."""
    for a,b,c in WINS:
        if board[a] and board[a]==board[b]==board[c]:
            return board[a]
    return None

def is_draw(board):
    return None not in board and check_winner(board) is None

def available(board):
    return [i for i,v in enumerate(board) if v is None]

# ─── HEURISTIC EVALUATION (Easy Mode) ────────────────────────────────────────
# Priority: win > center > corner > edge
def heuristic_move(board, ai_mark, human_mark):
    moves = available(board)

    # 1) Win immediately
    for m in moves:
        b = board[:]
        b[m] = ai_mark
        if check_winner(b) == ai_mark:
            return m
    
    # 2) Prefer center
    if 4 in moves:
        return 4

    # 3) Prefer corners
    for c in [0,2,6,8]:
        if c in moves:
            return c

    # 4) Prefer edges
    for e in [1,3,5,7]:
        if e in moves:
            return e

    return moves[0]

# ─── MINIMAX ALGORITHM (Hard Mode) ───────────────────────────────────────────
def minimax(board, is_maximizing, ai_mark, human_mark):
    winner = check_winner(board)
    if winner == ai_mark:    return  1
    if winner == human_mark: return -1
    if is_draw(board):       return  0

    if is_maximizing:
        best = -math.inf
        for m in available(board):
            b = board[:]
            b[m] = ai_mark
            best = max(best, minimax(b, False, ai_mark, human_mark))
        return best
    else:
        best = math.inf
        for m in available(board):
            b = board[:]
            b[m] = human_mark
            best = min(best, minimax(b, True, ai_mark, human_mark))
        return best

def best_move_minimax(board, ai_mark, human_mark):
    best_val, best_m = -math.inf, None
    for m in available(board):
        b = board[:]
        b[m] = ai_mark
        val = minimax(b, False, ai_mark, human_mark)
        if val > best_val:
            best_val, best_m = val, m
    return best_m

# ─── ALPHA-BETA PRUNING (Hard Mode Optimized) ────────────────────────────────
def minimax_ab(board, is_maximizing, ai_mark, human_mark, alpha, beta):
    winner = check_winner(board)
    if winner == ai_mark:    return  1
    if winner == human_mark: return -1
    if is_draw(board):       return  0

    if is_maximizing:
        best = -math.inf
        for m in available(board):
            b = board[:]
            b[m] = ai_mark
            best = max(best, minimax_ab(b, False, ai_mark, human_mark, alpha, beta))
            alpha = max(alpha, best)
            if beta <= alpha:           # Prune
                break
        return best
    else:
        best = math.inf
        for m in available(board):
            b = board[:]
            b[m] = human_mark
            best = min(best, minimax_ab(b, True, ai_mark, human_mark, alpha, beta))
            beta = min(beta, best)
            if beta <= alpha:           # Prune
                break
        return best

def best_move_ab(board, ai_mark, human_mark):
    best_val, best_m = -math.inf, None
    for m in available(board):
        b = board[:]
        b[m] = ai_mark
        val = minimax_ab(b, False, ai_mark, human_mark, -math.inf, math.inf)
        if val > best_val:
            best_val, best_m = val, m
    return best_m

# ─── DRAWING HELPERS ──────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, r=12, border_color=None, border_w=2):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_w, border_radius=r)

def draw_button(surf, text, rect, hover=False, color=None, text_col=WHITE):
    bg = color if color else (BTN_HOVER if hover else BTN_MAIN)
    draw_rounded_rect(surf, bg, rect, r=10, border_color=BTN_BORDER)
    lbl = BTN_FONT.render(text, True, text_col)
    surf.blit(lbl, (rect[0]+(rect[2]-lbl.get_width())//2,
                    rect[1]+(rect[3]-lbl.get_height())//2))

def draw_grid():
    ox, oy = 60, BOARD_TOP
    for i in range(1,3):
        pygame.draw.line(screen, GRID_COL,
                         (ox + i*CELL, oy), (ox + i*CELL, oy+3*CELL), LINE_W)
        pygame.draw.line(screen, GRID_COL,
                         (ox, oy + i*CELL), (ox+3*CELL, oy + i*CELL), LINE_W)

def cell_center(idx):
    ox, oy = 60, BOARD_TOP
    r, c = divmod(idx, 3)
    return ox + c*CELL + CELL//2, oy + r*CELL + CELL//2

def draw_mark(mark, idx, alpha=255):
    cx, cy = cell_center(idx)
    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    if mark == 'O':
        pygame.draw.circle(surf, (*O_COL, alpha), (CELL//2, CELL//2), CIRCLE_R, CIRCLE_W)
    else:
        off = CROSS_OFF
        pygame.draw.line(surf, (*X_COL, alpha),
                         (off, off), (CELL-off, CELL-off), CROSS_W)
        pygame.draw.line(surf, (*X_COL, alpha),
                         (CELL-off, off), (off, CELL-off), CROSS_W)
    screen.blit(surf, (cx - CELL//2, cy - CELL//2))

def draw_board(board):
    draw_grid()
    for i, v in enumerate(board):
        if v:
            draw_mark(v, i)

def winning_cells(board):
    for a,b,c in WINS:
        if board[a] and board[a]==board[b]==board[c]:
            return (a,b,c)
    return None

def draw_win_line(board):
    cells = winning_cells(board)
    if not cells:
        return
    p1 = cell_center(cells[0])
    p2 = cell_center(cells[2])
    col = X_COL if board[cells[0]] == 'X' else O_COL
    pygame.draw.line(screen, col, p1, p2, 8)

def draw_status(text, col=WHITE):
    lbl = STATUS_FONT.render(text, True, col)
    screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 68))

def draw_title():
    t = TITLE_FONT.render("TIC  TAC  TOE", True, WHITE)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 10))

# ─── OVERLAY POPUP (AI vs AI sub-menu) ───────────────────────────────────────
def draw_popup(hover_idx):
    # dim background
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill(OVERLAY)
    screen.blit(dim, (0,0))

    # Taller popup to accommodate 5 options
    pw, ph = 460, 400
    px, py = (WIDTH-pw)//2, (HEIGHT-ph)//2
    draw_rounded_rect(screen, RESULT_BG, (px,py,pw,ph), r=18,
                      border_color=AIVA_COL, border_w=2)

    title = LABEL_FONT.render("AI  VS  AI  —  SELECT  MODE", True, AIVA_COL)
    screen.blit(title, (px+(pw-title.get_width())//2, py+18))

    options = [
        ("EASY  vs  EASY",               EASY_COL),
        ("HARD  vs  HARD  (Minimax)",    HARD_COL),
        ("EASY (X)  vs  HARD (O)",       WHITE),
        ("HARD (X)  vs  EASY (O)",       WHITE),       # ← new
        ("HARD  vs  HARD  (Alpha-Beta)", HARD_COL),
    ]
    rects = []
    for i,(label,col) in enumerate(options):
        r = pygame.Rect(px+30, py+70+i*58, pw-60, 44)
        rects.append(r)
        hov = (i == hover_idx)
        draw_button(screen, label, r, hover=hov, text_col=col)

    close = SMALL_FONT.render("click outside to close", True, GRAY)
    screen.blit(close, (px+(pw-close.get_width())//2, py+ph-24))
    return rects, (px,py,pw,ph)

# ─── AI vs AI SIMULATION ─────────────────────────────────────────────────────
def run_ai_vs_ai(mode):
    """
    mode: 'ee' easy-easy | 'hh_mm' hard-hard minimax |
          'eh' easy(X)-hard(O) | 'he' hard(X)-easy(O) |
          'hh_ab' hard-hard alpha-beta
    """
    results = {"X":0, "O":0, "Draw":0}
    total_time = {"X":0.0, "O":0.0}

    N = 10

    if mode == 'ee':
        def move_x(b): return heuristic_move(b,'X','O')
        def move_o(b): return heuristic_move(b,'O','X')
        label = "EASY vs EASY"
    elif mode == 'hh_mm':
        def move_x(b): return best_move_minimax(b,'X','O')
        def move_o(b): return best_move_minimax(b,'O','X')
        label = "HARD vs HARD  (Minimax)"
    elif mode == 'eh':
        def move_x(b): return heuristic_move(b,'X','O')
        def move_o(b): return best_move_ab(b,'O','X')
        label = "EASY (X) vs HARD (O)"
    elif mode == 'he':                                  # ← new
        def move_x(b): return best_move_ab(b,'X','O')
        def move_o(b): return heuristic_move(b,'O','X')
        label = "HARD (X) vs EASY (O)"
    else:  # hh_ab
        def move_x(b): return best_move_ab(b,'X','O')
        def move_o(b): return best_move_ab(b,'O','X')
        label = "HARD vs HARD  (Alpha-Beta)"

    for _ in range(N):
        board = empty_board()
        turn  = 'X'
        while True:
            t0 = time.perf_counter()
            if turn == 'X':
                m = move_x(board)
            else:
                m = move_o(board)
            elapsed = time.perf_counter() - t0
            total_time[turn] += elapsed
            board[m] = turn
            w = check_winner(board)
            if w:
                results[w] += 1
                break
            if is_draw(board):
                results["Draw"] += 1
                break
            turn = 'O' if turn == 'X' else 'X'

    return label, results, total_time, N

# ─── RESULT SCREEN ────────────────────────────────────────────────────────────
def show_result_screen(label, results, times, N):
    waiting = True
    while waiting:
        screen.fill(BG)
        draw_title()

        pw, ph = 500, 360
        px, py = (WIDTH-pw)//2, (HEIGHT-ph)//2 - 10
        draw_rounded_rect(screen, RESULT_BG, (px,py,pw,ph), r=18,
                          border_color=AIVA_COL, border_w=2)

        t = LABEL_FONT.render(label, True, AIVA_COL)
        screen.blit(t, (px+(pw-t.get_width())//2, py+16))

        lines = [
            (f"Games played : {N}",             WHITE),
            (f"X  wins      : {results['X']}",  X_COL),
            (f"O  wins      : {results['O']}",  O_COL),
            (f"Draws        : {results['Draw']}", GRAY),
        ]
        if times['X'] > 0 or times['O'] > 0:
            lines.append((f"X  total time: {times['X']*1000:.1f} ms", X_COL))
            lines.append((f"O  total time: {times['O']*1000:.1f} ms", O_COL))

        for i,(txt,col) in enumerate(lines):
            lbl = BTN_FONT.render(txt, True, col)
            screen.blit(lbl, (px+40, py+65+i*38))

        back_r = pygame.Rect(px+(pw-180)//2, py+ph-56, 180, 40)
        mx,my  = pygame.mouse.get_pos()
        hov    = back_r.collidepoint(mx,my)
        draw_button(screen, "BACK  TO  MENU", back_r, hover=hov)

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if back_r.collidepoint(ev.pos):
                    waiting = False
        clock.tick(60)

# ─── PLAY GAME (User vs AI or AI vs AI animated) ─────────────────────────────
def play_game(mode_label, player_x_fn, player_o_fn, human_player=None):
    """
    human_player: 'X' | 'O' | None  (None = both AI)
    player_x_fn / player_o_fn: callable(board) -> index
    """
    board     = empty_board()
    turn      = 'X'
    game_over = False
    winner    = None
    ai_delay  = 0       # frames before AI acts (for visual pause)

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)
        draw_title()
        draw_board(board)

        if not game_over:
            if turn == human_player:
                draw_status("YOUR  TURN", WHITE)
            else:
                mark_col = X_COL if turn=='X' else O_COL
                draw_status(f"AI  THINKING  ({turn})...", mark_col)
        else:
            if winner:
                col = X_COL if winner=='X' else O_COL
                who = "YOU  WIN!" if winner==human_player else (
                      "AI  WINS!" if human_player else f"{winner}  WINS!")
                draw_status(who, col)
                draw_win_line(board)
            else:
                draw_status("DRAW!", GRAY)

        back_r = pygame.Rect(20, HEIGHT-54, 130, 38)
        draw_button(screen, "← MENU", back_r,
                    hover=back_r.collidepoint(mx,my))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if back_r.collidepoint(ev.pos):
                    return
                if not game_over and turn == human_player:
                    ox, oy = 60, BOARD_TOP
                    gx, gy = ev.pos[0]-ox, ev.pos[1]-oy
                    if 0<=gx<3*CELL and 0<=gy<3*CELL:
                        col_i, row_i = gx//CELL, gy//CELL
                        idx = row_i*3 + col_i
                        if board[idx] is None:
                            board[idx] = turn
                            w = check_winner(board)
                            if w or is_draw(board):
                                winner = w
                                game_over = True
                            else:
                                turn = 'O' if turn=='X' else 'X'
                                ai_delay = 30
            if ev.type == pygame.KEYDOWN and game_over:
                if ev.key == pygame.K_r:
                    return play_game(mode_label, player_x_fn, player_o_fn, human_player)

        if not game_over and turn != human_player:
            ai_delay -= 1
            if ai_delay <= 0:
                fn = player_x_fn if turn=='X' else player_o_fn
                m  = fn(board)
                board[m] = turn
                w = check_winner(board)
                if w or is_draw(board):
                    winner = w
                    game_over = True
                else:
                    turn = 'O' if turn=='X' else 'X'
                    ai_delay = 30 if human_player else 45

        clock.tick(60)

# ─── MAIN MENU ────────────────────────────────────────────────────────────────
def main_menu():
    popup_open = False
    popup_hover = -1

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        for x in range(0, WIDTH, 60):
            pygame.draw.line(screen, (25,25,35), (x,0), (x,HEIGHT))
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(screen, (25,25,35), (0,y), (WIDTH,y))

        draw_title()
        sub = SMALL_FONT.render("by  Kush Bajaria  &  AP Calderon", True, GRAY)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 68))

        easy_r  = pygame.Rect(100, 200, 400, 56)
        hard_r  = pygame.Rect(100, 276, 400, 56)
        aivai_r = pygame.Rect(100, 380, 400, 56)

        draw_button(screen, "EASY  MODE  (User vs AI)",
                    easy_r,  hover=easy_r.collidepoint(mx,my),
                    text_col=EASY_COL)
        draw_button(screen, "HARD  MODE  (User vs AI)",
                    hard_r,  hover=hard_r.collidepoint(mx,my),
                    text_col=HARD_COL)
        draw_button(screen, "AI  VS  AI",
                    aivai_r, hover=aivai_r.collidepoint(mx,my),
                    text_col=AIVA_COL)

        legend_y = 460
        for i,(txt,col) in enumerate([
            ("EASY : Heuristic evaluation  (win / block / center / corner / edge)", EASY_COL),
            ("HARD : Minimax  +  Alpha-Beta Pruning — unbeatable",                  HARD_COL),
            ("AI vs AI : simulation with timing stats",                             AIVA_COL),
        ]):
            lbl = SMALL_FONT.render(txt, True, col)
            screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, legend_y + i*22))

        popup_rects = None
        popup_area  = None
        if popup_open:
            popup_rects, popup_area = draw_popup(popup_hover)
            popup_hover = -1
            for i,r in enumerate(popup_rects):
                if r.collidepoint(mx,my):
                    popup_hover = i

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if popup_open:
                    px,py,pw,ph = popup_area
                    if not pygame.Rect(px,py,pw,ph).collidepoint(ev.pos):
                        popup_open = False
                    else:
                        for i,r in enumerate(popup_rects):
                            if r.collidepoint(ev.pos):
                                popup_open = False
                                # Maps button index → mode key (5 options now)
                                modes = ['ee', 'hh_mm', 'eh', 'he', 'hh_ab']
                                screen.fill(BG)
                                loading = LABEL_FONT.render("RUNNING SIMULATION...", True, AIVA_COL)
                                screen.blit(loading, (WIDTH//2-loading.get_width()//2, HEIGHT//2))
                                pygame.display.flip()
                                label, res, times, N = run_ai_vs_ai(modes[i])
                                show_result_screen(label, res, times, N)
                else:
                    if easy_r.collidepoint(ev.pos):
                        play_game(
                            "Easy",
                            lambda b: None,
                            lambda b: heuristic_move(b,'O','X'),
                            human_player='X'
                        )
                    elif hard_r.collidepoint(ev.pos):
                        play_game(
                            "Hard",
                            lambda b: None,
                            lambda b: best_move_ab(b,'O','X'),
                            human_player='X'
                        )
                    elif aivai_r.collidepoint(ev.pos):
                        popup_open = True
                        popup_hover = -1

        clock.tick(60)

# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main_menu()