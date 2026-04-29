import pygame
import sys
import math
import time

pygame.init()

# CONSTANTS
WIDTH, HEIGHT = 600, 700
BOARD_TOP    = 120
CELL         = 160
LINE_W       = 5
CIRCLE_R     = 55
CIRCLE_W     = 12
CROSS_W      = 15
CROSS_OFF    = 40

BG           = (245, 242, 235)
PANEL        = (255, 253, 248)
INK          = ( 32,  32,  38)
INK_SOFT     = ( 90,  90,  98)
RULE         = (210, 205, 195)
GRID_COL     = ( 60,  60,  70)
X_COL        = (200,  60,  55)
O_COL        = ( 30,  90, 160)
ACCENT       = (170, 130,  60)
BTN_MAIN     = (255, 253, 248)
BTN_HOVER    = (240, 235, 222)
BTN_BORDER   = ( 32,  32,  38)
EASY_COL     = ( 60, 120,  70)
HARD_COL     = (200,  60,  55)
AIVA_COL     = ( 90,  60, 140)
WHITE        = (250, 248, 242)
GRAY         = (140, 138, 132)
OVERLAY      = ( 32,  32,  38, 180)
RESULT_BG    = (255, 253, 248)

# Font stack — try system fonts, fall back otherwise.
SERIF_STACK  = "PlayfairDisplay,Baskerville,Didot,Georgia,Garamond,serif"
SANS_STACK   = "HelveticaNeue,Helvetica,Avenir,Inter,Arial,sans-serif"
MONO_STACK   = "JetBrainsMono,IBMPlexMono,Menlo,Consolas,Courier New,monospace"

TITLE_FONT   = pygame.font.SysFont(SERIF_STACK, 64, bold=False, italic=False)
SUB_FONT     = pygame.font.SysFont(SERIF_STACK, 18, italic=True)
LABEL_FONT   = pygame.font.SysFont(SANS_STACK,  16, bold=True)
BTN_FONT     = pygame.font.SysFont(SANS_STACK,  17, bold=True)
STATUS_FONT  = pygame.font.SysFont(SERIF_STACK, 28, bold=False)
SMALL_FONT   = pygame.font.SysFont(SANS_STACK,  13)
TINY_FONT    = pygame.font.SysFont(SANS_STACK,  11, bold=True)
TIMER_FONT   = pygame.font.SysFont(MONO_STACK,  16, bold=True)

# Home-screen
HOME_TITLE   = pygame.font.SysFont(SERIF_STACK, 76, italic=False)
HOME_SUB     = pygame.font.SysFont(SERIF_STACK, 17, italic=True)
HOME_KICKER  = pygame.font.SysFont(SANS_STACK,  10, bold=True)
HOME_BTN     = pygame.font.SysFont(SANS_STACK,  15, bold=True)
HOME_BTN_SUB = pygame.font.SysFont(SERIF_STACK, 13, italic=True)
HOME_NUM     = pygame.font.SysFont(SERIF_STACK, 26, italic=True)
HOME_META    = pygame.font.SysFont(SANS_STACK,  11)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
clock  = pygame.time.Clock()

# GAME STATE REPRESENTATION
# Board is a list of 9 cells: 'X', 'O', or None
WINS = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # columns
    (0,4,8),(2,4,6)            # diagonals
]

# Clears board
def empty_board():
    return [None]*9

# Loop unpacks each triple into three indices (a,b,c) checks if
# their position is in WINS
def check_winner(board):
    """Return 'X', 'O', or None."""
    for a,b,c in WINS:
        if board[a] and board[a]==board[b]==board[c]:
            return board[a]
    return None

# If the board tied
def is_draw(board):
    return None not in board and check_winner(board) is None

# returns the indices of empty cells so ai can know open positions
def available(board):
    return [i for i,v in enumerate(board) if v is None]

# HEURISTIC RULES BASED EVALUATION (Easy Mode)
# Priority: win > center > corner > edge
def heuristic_move(board, ai_mark, human_mark):
    moves = available(board)

    # 1) Win immediately
    for m in moves:
        # copy of board so ai can replicate the move
        b = board[:]
        b[m] = ai_mark
        if check_winner(b) == ai_mark:
            return m
    
    # 2) Prefer center
    # 4 is the middle of the board in terms of positional reference
    if 4 in moves:
        return 4

    # 3) Prefer corners
    # 0,2,6,8 are the corners of the board in terms of positional reference
    for c in [0,2,6,8]:
        if c in moves:
            return c

    # 4) Prefer edges
    # 1,3,5,7 are the edges of the board in terms of positional reference from the center
    for e in [1,3,5,7]:
        if e in moves:
            return e

    # fallback
    return moves[0]

# MINIMAX ALGORITHM (Hard Mode)
def minimax(board, is_maximizing, ai_mark, human_mark):
    winner = check_winner(board)
    if winner == ai_mark:
        return 1
    if winner == human_mark:
        return -1
    if is_draw(board):
        return 0

    # AIs turn
    if is_maximizing:
        best = -math.inf
        for m in available(board):
            # copy of board so ai can replicate the move
            b = board[:]
            # try this move (m)
            b[m] = ai_mark
            best = max(best, minimax(b, False, ai_mark, human_mark))
        return best
    # User's turn (takes worst outcome for ai since user is assumed to play optimally)
    else:
        best = math.inf
        for m in available(board):
            # copy of board so ai can replicate the move
            b = board[:]
            b[m] = human_mark
            best = min(best, minimax(b, True, ai_mark, human_mark))
        # takes users best score (worse for ai)
        return best

def best_move_minimax(board, ai_mark, human_mark):
    # starts with worst possible score and no moves choosen
    best_val, best_m = -math.inf, None
    for m in available(board):
        # copy of board so ai can replicate the move
        b = board[:]
        b[m] = ai_mark
        val = minimax(b, False, ai_mark, human_mark)
        if val > best_val:
            best_val, best_m = val, m
    # loop above gets the position of the move that returned the highest score

    # return the position with highest score
    return best_m

# MINIMAX WITH ALPHA-BETA PRUNING (Hard Mode Optimized)
def minimax_ab(board, is_maximizing, ai_mark, human_mark, alpha, beta):
    winner = check_winner(board)
    if winner == ai_mark:
        return  1
    if winner == human_mark:
        return -1
    if is_draw(board):
        return  0

    if is_maximizing:
        best = -math.inf
        for m in available(board):
            # copy of board so ai can replicate the move
            b = board[:]
            b[m] = ai_mark
            best = max(best, minimax_ab(b, False, ai_mark, human_mark, alpha, beta))
            alpha = max(alpha, best)
            # minimizer already has a path elsewhere that's better than anything this branch
            # can offer, so the remaining moves are skipped.
            if beta <= alpha:           # Prune
                break
        return best
    else:
        best = math.inf
        for m in available(board):
            # copy of board so ai can replicate the move
            b = board[:]
            b[m] = human_mark
            best = min(best, minimax_ab(b, True, ai_mark, human_mark, alpha, beta))
            beta = min(beta, best)
            # maximizer already has a guaranteed path that's better than this branch can deliver, prune it.
            if beta <= alpha:           # Prune
                break
        return best

def best_move_ab(board, ai_mark, human_mark):
    # starts with worst possible score and no moves choosen
    best_val, best_m = -math.inf, None
    for m in available(board):
        # copy of board so ai can replicate the move
        b = board[:]
        b[m] = ai_mark
        val = minimax_ab(b, False, ai_mark, human_mark, -math.inf, math.inf)
        if val > best_val:
            best_val, best_m = val, m
    # loop above gets the position of the move that returned the highest score

    # return the position with highest score
    return best_m

# DRAWING HELPERS
def draw_rounded_rect(surf, color, rect, r=12, border_color=None, border_w=2):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, border_w, border_radius=r)

def draw_button(surf, text, rect, hover=False, color=None, text_col=None):
    bg = color if color else (BTN_HOVER if hover else BTN_MAIN)
    draw_rounded_rect(surf, bg, rect, r=10, border_color=BTN_BORDER)
    lbl = BTN_FONT.render(text, True, text_col if text_col is not None else INK)
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

def draw_status(text, col=None):
    lbl = STATUS_FONT.render(text, True, col if col is not None else INK)
    screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 68))

def draw_title():
    t = TITLE_FONT.render("Tic-Tac-Toe", True, INK)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 5))

# AI vs AI sub-menu
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
        ("EASY (X)  vs  HARD (O)",       INK),
        ("HARD (X)  vs  EASY (O)",       INK),
        ("HARD  vs  HARD  (Minimax)",    HARD_COL),
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

# AI vs AI SIMULATION
def run_ai_vs_ai(mode):
    """
    mode: 'ee' easy-easy | 'eh' easy(X)-hard(O) |
          'he' hard(X)-easy(O) | 'hh_mm' hard-hard minimax |
          'hh_ab' hard-hard alpha-beta
    """
    results = {"X":0, "O":0, "Draw":0}
    total_time = {"X":0.0, "O":0.0}

    N = 100

    if mode == 'ee':
        def move_x(b): return heuristic_move(b,'X','O')
        def move_o(b): return heuristic_move(b,'O','X')
        label = "EASY vs EASY"
    elif mode == 'eh':
        def move_x(b): return heuristic_move(b,'X','O')
        def move_o(b): return best_move_ab(b,'O','X')
        label = "EASY (X) vs HARD (O)"
    elif mode == 'he':
        def move_x(b): return best_move_ab(b,'X','O')
        def move_o(b): return heuristic_move(b,'O','X')
        label = "HARD (X) vs EASY (O)"
    elif mode == 'hh_mm':
        def move_x(b): return best_move_minimax(b,'X','O')
        def move_o(b): return best_move_minimax(b,'O','X')
        label = "HARD vs HARD  (Minimax)"
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

# RESULT SCREEN
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
            (f"Games played : {N}",             INK),
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

# PLAY GAME (User vs AI or AI vs AI animated)
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
                draw_status("YOUR  TURN", INK)
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

# MAIN MENU
def draw_motif(cx, cy, size=64):
    """Small decorative tic-tac-toe glyph with an X and an O placed inside."""
    s = size
    half = s // 2
    third = s // 3
    x0, y0 = cx - half, cy - half
    # grid (hairline)
    for i in (1, 2):
        pygame.draw.line(screen, INK_SOFT, (x0 + i*third, y0), (x0 + i*third, y0 + s), 1)
        pygame.draw.line(screen, INK_SOFT, (x0, y0 + i*third), (x0 + s, y0 + i*third), 1)
    # X in top-left cell
    pad = third // 4
    cell0 = pygame.Rect(x0, y0, third, third)
    pygame.draw.line(screen, X_COL,
                     (cell0.left+pad, cell0.top+pad),
                     (cell0.right-pad, cell0.bottom-pad), 2)
    pygame.draw.line(screen, X_COL,
                     (cell0.right-pad, cell0.top+pad),
                     (cell0.left+pad, cell0.bottom-pad), 2)
    # O in bottom-right cell
    cell8 = pygame.Rect(x0 + 2*third, y0 + 2*third, third, third)
    pygame.draw.circle(screen, O_COL, cell8.center, third//2 - pad, 2)

def draw_card_button(rect, num, title, subtitle, accent, hover):
    """Paper-card button with a serif numeral, sans title, italic-serif subtitle."""
    bg = BTN_HOVER if hover else PANEL
    draw_rounded_rect(screen, bg, rect, r=4, border_color=INK, border_w=1)
    # Vertical accent bar on the left
    bar = pygame.Rect(rect.x, rect.y, 4, rect.h)
    pygame.draw.rect(screen, accent, bar)
    # Serif numeral
    n = HOME_NUM.render(num, True, INK_SOFT)
    screen.blit(n, (rect.x + 22, rect.y + (rect.h - n.get_height())//2 - 1))
    # Title (sans, tracked)
    t = HOME_BTN.render(title, True, INK)
    screen.blit(t, (rect.x + 70, rect.y + 14))
    # Subtitle (italic serif)
    s = HOME_BTN_SUB.render(subtitle, True, INK_SOFT)
    screen.blit(s, (rect.x + 70, rect.y + 14 + t.get_height() + 2))
    # Right-side caret on hover
    if hover:
        cx = rect.right - 22
        cy = rect.y + rect.h//2
        pygame.draw.line(screen, INK, (cx-6, cy-5), (cx, cy), 2)
        pygame.draw.line(screen, INK, (cx-6, cy+5), (cx, cy), 2)

def main_menu():
    popup_open = False
    popup_hover = -1

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)

        # ── Top kicker (small caps, tracked) ──
        kicker = "CPSC 481  ·  ARTIFICIAL INTELLIGENCE"
        k = HOME_KICKER.render(kicker, True, INK_SOFT)
        screen.blit(k, (WIDTH//2 - k.get_width()//2, 36))

        # Hairline rule under kicker
        pygame.draw.line(screen, RULE, (60, 58), (WIDTH-60, 58), 1)

        # ── Title (large serif) ──
        title = HOME_TITLE.render("Tic-Tac-Toe", True, INK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 78))

        # ── Italic subtitle (removed for now) ──
        sub_txt = ""
        sub = HOME_SUB.render(sub_txt, True, INK_SOFT)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 78 + title.get_height() + 2))

        # Decorative motif under subtitle
        motif_y = 78 + title.get_height() + sub.get_height() + 32
        draw_motif(WIDTH//2, motif_y, size=46)

        # Hairline rule above buttons
        rule_y = motif_y + 44
        pygame.draw.line(screen, RULE, (60, rule_y), (WIDTH-60, rule_y), 1)

        # ── Three card-style buttons ──
        btn_w, btn_h = 440, 72
        btn_x = (WIDTH - btn_w)//2
        easy_r  = pygame.Rect(btn_x, rule_y + 24,             btn_w, btn_h)
        hard_r  = pygame.Rect(btn_x, easy_r.bottom + 14,      btn_w, btn_h)
        aivai_r = pygame.Rect(btn_x, hard_r.bottom + 14,      btn_w, btn_h)

        draw_card_button(easy_r,  "I.",   "EASY MODE",
                         "you versus a heuristic agent",
                         EASY_COL, easy_r.collidepoint(mx, my))
        draw_card_button(hard_r,  "II.",  "HARD MODE",
                         "you versus minimax with α-β pruning",
                         HARD_COL, hard_r.collidepoint(mx, my))
        draw_card_button(aivai_r, "III.", "AGENT VS AGENT",
                         "simulate matchups & view timing data",
                         AIVA_COL, aivai_r.collidepoint(mx, my))

        # ── Footer ──
        foot_y = HEIGHT - 44
        pygame.draw.line(screen, RULE, (60, foot_y - 14), (WIDTH-60, foot_y - 14), 1)
        byline = HOME_META.render("Kush Bajaria  ·  AP Calderon", True, INK_SOFT)
        screen.blit(byline, (60, foot_y))
        right = HOME_META.render("California State University, Fullerton", True, INK_SOFT)
        screen.blit(right, (WIDTH - 60 - right.get_width(), foot_y))

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
                                modes = ['ee', 'eh', 'he', 'hh_mm', 'hh_ab']
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

# ENTRY POINT
if __name__ == "__main__":
    main_menu()