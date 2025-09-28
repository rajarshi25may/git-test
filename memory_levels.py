# Progressive Memory Game – multi-level, full-image cover
# - Counts every left-click as a move
# - 1s mismatch delay, 2s level-advance delay
# - HUD + per-level move counts
# - Mini report card persists during the 2s pause
# - Final Report Card at the end

from random import shuffle
from turtle import *

# ---------- levels: (cols, rows, background gif) ----------
LEVELS = [
    (2, 2, "images/cycle.gif"),       # Level 1  🚲
    (3, 4, "images/scooter.gif"),     # Level 2  🛵
    (4, 4, "images/car.gif"),         # Level 3  🚗
    (5, 4, "images/helicopter.gif"),  # Level 4  🚁
    (6, 6, "images/jet.gif"),         # Level 5  ✈
    (8, 8, "images/rocket.gif"),      # Level 6  🚀
    (10,10,"images/spaceship.gif"),   # Level 7  🛸
]
# -----------------------------------------------------------

WIN_W, WIN_H = 800, 600     # window; grid auto-fits to fill this
FONT = ('Arial', 20, 'normal')
HUD_FONT = ('Arial', 16, 'bold')
BANNER_FONT = ('Arial', 22, 'bold')
REPORT_FONT = ('Arial', 16, 'normal')

# runtime state
level_idx = 0
COLS = ROWS = N = 0
TILE = 0
LEFT = BOTTOM = 0
tiles = []
hide = []
move_count = 0
level_results = []  # [{'level':1,'cols':2,'rows':2,'moves':N}, ...]

state = {
    'mark': None,          # first flipped index (not yet matched)
    'pending_hide': None,  # (a,b) mismatched pair to hide after delay
    'advancing': False,    # True while waiting 2s to switch levels
    'finished': False,     # True after last level
    'recorded': False,     # set True once we record this level's result
}

def size_grid(cols: int, rows: int):
    """Choose TILE so cols*tile x rows*tile exactly fills window (centered)."""
    global TILE, LEFT, BOTTOM
    TILE = min(WIN_W // cols, WIN_H // rows)
    board_w = cols * TILE
    board_h = rows * TILE
    LEFT   = -board_w // 2
    BOTTOM = -board_h // 2

def setup_level(idx: int):
    """Initialize a level by index."""
    global COLS, ROWS, N, tiles, hide, move_count
    state['advancing'] = False
    state['pending_hide'] = None
    state['mark'] = None
    state['recorded'] = False

    COLS, ROWS, bg = LEVELS[idx]
    N = COLS * ROWS
    move_count = 0

    size_grid(COLS, ROWS)

    setup(WIN_W, WIN_H)
    title(f"Memory – Level {idx+1}/{len(LEVELS)} ({COLS}×{ROWS})")

    try:
        bgpic(bg)  # set background image (gif)
    except Exception as e:
        print(f"[WARN] Could not load background {bg}: {e}")

    tiles = list(range(N // 2)) * 2
    shuffle(tiles)
    hide = [True] * N

    tracer(False)
    hideturtle()
    onscreenclick(tap)

def square(x, y, fill='#e6e6e6', border='black'):
    """Draw a filled square (tile cover) at (x, y)."""
    up(); goto(x, y); down()
    color(border, fill)
    begin_fill()
    for _ in range(4):
        forward(TILE); left(90)
    end_fill()

def index_from_xy(x, y):
    """Map screen coords to tile index or None if out of bounds."""
    col = int((x - LEFT) // TILE)
    row = int((y - BOTTOM) // TILE)
    if 0 <= col < COLS and 0 <= row < ROWS:
        return row * COLS + col
    return None

def xy_from_index(i):
    """Map tile index to top-left screen coords."""
    col = i % COLS
    row = i // COLS
    return LEFT + col * TILE, BOTTOM + row * TILE

def tap(x, y):
    """Every valid click counts as a move; then flip/match logic with delays."""
    global move_count
    if state['finished'] or state['advancing'] or state['pending_hide']:
        return

    spot = index_from_xy(x, y)
    if spot is None or not hide[spot]:
        return

    # Count every left-click that flips a tile
    move_count += 1

    mark = state['mark']
    if mark is None or mark == spot:
        state['mark'] = spot
        return

    # second click of an attempt
    if tiles[mark] == tiles[spot]:
        hide[spot] = hide[mark] = False
        state['mark'] = None
    else:
        state['pending_hide'] = (mark, spot)
        state['mark'] = None
        ontimer(hide_pending, 1000)  # 1-second flip-back

def hide_pending():
    if state['pending_hide']:
        a, b = state['pending_hide']
        hide[a] = True
        hide[b] = True
        state['pending_hide'] = None

def all_revealed():
    return all(not h for h in hide)

def advance_after_delay():
    """Advance to next level after the 2s pause."""
    global level_idx
    level_idx += 1
    if level_idx < len(LEVELS):
        setup_level(level_idx)
    else:
        state['finished'] = True

def draw_hud():
    """Top progress text."""
    up()
    goto(0, WIN_H//2 - 30)
    color('black')
    write(f"Level {level_idx+1} / {len(LEVELS)}",
          align='center', font=HUD_FONT)

def draw_grid_outline():
    """Faint grid so the board is always visible."""
    color('#999999'); width(1)
    # horizontal lines
    for r in range(ROWS+1):
        up(); goto(LEFT, BOTTOM + r*TILE); down()
        forward(COLS*TILE)
    right(90)
    # vertical lines
    for c in range(COLS+1):
        up(); goto(LEFT + c*TILE, BOTTOM); down()
        forward(ROWS*TILE)
    left(90)

def draw_results_panel():
    """Show results collected so far (left-top)."""
    if not level_results:
        return
    margin_x = LEFT
    margin_y = WIN_H//2 - 60
    up(); goto(margin_x + 10, margin_y)
    color('black')
    write("Results so far:", align='left', font=HUD_FONT)
    y = margin_y - 22
    for res in level_results[-6:]:  # show last up to 6 lines
        txt = f"Lvl {res['level']}: {res['cols']}x{res['rows']} → {res['moves']} moves"
        up(); goto(margin_x + 10, y)
        write(txt, align='left', font=REPORT_FONT)
        y -= 20

def record_level_if_needed():
    """Record the just-finished level's move count once."""
    if not state['recorded']:
        cols, rows, _ = LEVELS[level_idx]
        level_results.append({
            'level': level_idx + 1,
            'cols': cols,
            'rows': rows,
            'moves': move_count,
        })
        state['recorded'] = True

def draw_level_complete_overlay():
    """Persistent overlay shown during the 2s pause before advancing."""
    # Banner
    up(); goto(0, -WIN_H//2 + 30)
    color('blue')
    moves_text = f"Level {level_idx+1} complete in {move_count} moves!"
    write(moves_text, align='center', font=BANNER_FONT)
    # Side panel with results so far
    draw_results_panel()

def draw_final_report():
    """Final report card after last level."""
    total = sum(r['moves'] for r in level_results)
    up(); goto(0, 40)
    color('blue'); write("📋 Report Card", align='center', font=BANNER_FONT)
    y = 10
    color('black')
    for res in level_results:
        line = f"Level {res['level']:>2} ({res['cols']}x{res['rows']}): {res['moves']} moves"
        up(); goto(0, y)
        write(line, align='center', font=REPORT_FONT)
        y -= 22
    up(); goto(0, y - 10)
    color('purple'); write(f"Total moves: {total}", align='center', font=('Arial', 18, 'bold'))

def draw():
    clear()

    draw_hud()

    # covers (only on hidden tiles)
    for i in range(N):
        if hide[i]:
            x, y = xy_from_index(i)
            square(x, y)

    draw_grid_outline()

    # current single mark
    mark = state['mark']
    if mark is not None and hide[mark]:
        x, y = xy_from_index(mark)
        up(); goto(x + TILE//2, y + TILE//2 - 10)
        color('black'); write(tiles[mark], align='center', font=FONT)

    # pending mismatch → show both numbers during the 1s wait
    if state['pending_hide']:
        a, b = state['pending_hide']
        for spot in (a, b):
            x, y = xy_from_index(spot)
            up(); goto(x + TILE//2, y + TILE//2 - 10)
            color('black'); write(tiles[spot], align='center', font=FONT)

    # Finished all levels?
    if state['finished']:
        draw_final_report()
        update()
        return

    # Level complete → record once, then keep overlay visible while advancing
    if all_revealed() and state['pending_hide'] is None:
        record_level_if_needed()
        # Start the 2s pause exactly once
        if not state['advancing']:
            state['advancing'] = True
            ontimer(advance_after_delay, 2000)
        # Draw the overlay EVERY FRAME until level actually changes
        draw_level_complete_overlay()

    update()
    ontimer(draw, 80)

# ---- run ----
setup(WIN_W, WIN_H)
setup_level(level_idx)
draw()
done()
