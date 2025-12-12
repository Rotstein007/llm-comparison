# tetris.py
import sys
import random
import pygame

# -------------------- Config --------------------
COLS, ROWS = 10, 20
CELL = 30
SIDE_PANEL = 220
TOP_MARGIN = 40
WIDTH = COLS * CELL + SIDE_PANEL
HEIGHT = ROWS * CELL + TOP_MARGIN
FPS = 60

BG = (15, 16, 18)
GRID_BG = (20, 22, 26)
GRID_LINE = (35, 38, 45)
TEXT = (230, 230, 230)
SUBTEXT = (170, 170, 170)

# Tetromino colors
COLORS = {
    "I": (80, 220, 220),
    "O": (235, 210, 80),
    "T": (185, 110, 235),
    "S": (110, 235, 120),
    "Z": (235, 110, 110),
    "J": (110, 150, 235),
    "L": (235, 160, 90),
}

# Rotations are lists of (x, y) block offsets in a 4x4 local grid.
SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (2, 2)],
    ],
    "T": [
        [(1, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (1, 3)],
        [(1, 1), (0, 2), (1, 2), (1, 3)],
    ],
    "S": [
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 1), (1, 2), (2, 2), (2, 3)],
        [(1, 2), (2, 2), (0, 3), (1, 3)],
        [(0, 1), (0, 2), (1, 2), (1, 3)],
    ],
    "Z": [
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 1), (1, 2), (2, 2), (1, 3)],
        [(0, 2), (1, 2), (1, 3), (2, 3)],
        [(1, 1), (0, 2), (1, 2), (0, 3)],
    ],
    "J": [
        [(0, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (2, 1), (1, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (2, 3)],
        [(1, 1), (1, 2), (0, 3), (1, 3)],
    ],
    "L": [
        [(2, 1), (0, 2), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (1, 3), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (0, 3)],
        [(0, 1), (1, 1), (1, 2), (1, 3)],
    ],
}


# -------------------- Helpers --------------------
def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag


def clamp(v, a, b):
    return max(a, min(b, v))


# -------------------- Game Objects --------------------
class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.rot = 0
        # Spawn near top center (local 4x4 grid, so x=3 is a nice start)
        self.x = 3
        self.y = -2  # allow spawn "above" visible field

    @property
    def color(self):
        return COLORS[self.kind]

    def blocks(self, rot=None, x=None, y=None):
        r = self.rot if rot is None else rot
        px = self.x if x is None else x
        py = self.y if y is None else y
        return [(px + bx, py + by) for (bx, by) in SHAPES[self.kind][r]]


class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.bag = new_bag()
        self.queue = []
        self._refill_queue()
        self.current = self._next_piece()
        self.next_piece = self._next_piece()
        self.game_over = False

        self.score = 0
        self.lines = 0
        self.level = 1

        self.drop_timer = 0.0
        self.lock_delay = 0.0
        self.paused = False

        # input repeat (DAS-like simple)
        self.move_repeat_timer = 0.0
        self.move_repeat_dir = 0  # -1 left, +1 right
        self.soft_drop = False

        # hard drop scoring
        self.last_drop_cells = 0

        if self._collides(self.current):
            self.game_over = True

    def _refill_queue(self):
        while len(self.queue) < 7:
            if not self.bag:
                self.bag = new_bag()
            self.queue.append(self.bag.pop())

    def _next_piece(self):
        self._refill_queue()
        return Piece(self.queue.pop(0))

    def _collides(self, piece, rot=None, x=None, y=None):
        for bx, by in piece.blocks(rot=rot, x=x, y=y):
            # Outside left/right or below bottom => collision
            if bx < 0 or bx >= COLS or by >= ROWS:
                return True
            # Above top is allowed (by < 0)
            if by >= 0 and self.grid[by][bx] is not None:
                return True
        return False

    def _merge_piece(self, piece):
        for bx, by in piece.blocks():
            if by < 0:
                self.game_over = True
                return
            self.grid[by][bx] = piece.color

    def _clear_lines(self):
        new_rows = []
        cleared = 0
        for row in self.grid:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_rows.append(row)
        while len(new_rows) < ROWS:
            new_rows.insert(0, [None for _ in range(COLS)])
        self.grid = new_rows
        return cleared

    def _update_level(self):
        self.level = 1 + self.lines // 10

    def drop_interval(self):
        # Simple speed curve: higher level => smaller interval
        # Clamp to avoid going too fast
        base = 0.75
        interval = base * (0.87 ** (self.level - 1))
        return clamp(interval, 0.05, 0.75)

    def rotate(self):
        if self.game_over or self.paused:
            return
        new_rot = (self.current.rot + 1) % 4

        # Very small "wall-kick" set (not full SRS, but feels decent)
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
        for kx, ky in kicks:
            nx, ny = self.current.x + kx, self.current.y + ky
            if not self._collides(self.current, rot=new_rot, x=nx, y=ny):
                self.current.rot = new_rot
                self.current.x, self.current.y = nx, ny
                return

    def move(self, dx):
        if self.game_over or self.paused:
            return
        nx = self.current.x + dx
        if not self._collides(self.current, x=nx, y=self.current.y):
            self.current.x = nx

    def step_down(self):
        """Try move down by 1. Returns True if moved, False if blocked."""
        ny = self.current.y + 1
        if not self._collides(self.current, x=self.current.x, y=ny):
            self.current.y = ny
            return True
        return False

    def hard_drop(self):
        if self.game_over or self.paused:
            return
        dropped = 0
        while self.step_down():
            dropped += 1
        # scoring: 2 points per hard drop cell (classic-ish)
        self.score += 2 * dropped
        self._lock_piece()

    def soft_drop_step(self):
        if self.step_down():
            self.score += 1  # 1 point per soft drop cell

    def _lock_piece(self):
        self._merge_piece(self.current)
        cleared = self._clear_lines()

        if cleared:
            # Scoring: (single, double, triple, tetris) * level
            line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += line_scores.get(cleared, 0) * self.level
            self.lines += cleared
            self._update_level()

        # Next pieces
        self.current = self.next_piece
        self.next_piece = self._next_piece()

        self.lock_delay = 0.0
        if self._collides(self.current):
            self.game_over = True

    def update(self, dt):
        if self.game_over or self.paused:
            return

        # Horizontal repeat movement
        if self.move_repeat_dir != 0:
            self.move_repeat_timer += dt
            # initial delay then faster repeat
            initial = 0.18
            repeat = 0.06
            if self.move_repeat_timer >= initial:
                while self.move_repeat_timer >= repeat:
                    self.move_repeat_timer -= repeat
                    self.move(self.move_repeat_dir)

        # Falling / dropping
        interval = self.drop_interval()
        if self.soft_drop:
            interval = min(interval, 0.05)

        self.drop_timer += dt
        while self.drop_timer >= interval:
            self.drop_timer -= interval
            moved = self.step_down()
            if not moved:
                # lock delay: allow a short time to rotate/move before locking
                self.lock_delay += interval
                if self.lock_delay >= 0.35:
                    self._lock_piece()
                    break
            else:
                self.lock_delay = 0.0

    def ghost_y(self):
        py = self.current.y
        while not self._collides(self.current, x=self.current.x, y=py + 1):
            py += 1
        return py


# -------------------- Rendering --------------------
def draw_cell(screen, x, y, color, alpha=255):
    r = pygame.Rect(x, y, CELL, CELL)
    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    surf.fill((*color, alpha))
    screen.blit(surf, r.topleft)
    pygame.draw.rect(screen, (0, 0, 0), r, 1)


def draw_text(screen, font, s, x, y, color=TEXT):
    img = font.render(s, True, color)
    screen.blit(img, (x, y))


def main():
    pygame.init()
    pygame.display.set_caption("Tetris (Python)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 22)
    big = pygame.font.SysFont("consolas", 36, bold=True)
    small = pygame.font.SysFont("consolas", 18)

    game = Tetris()

    def field_origin():
        return 0, TOP_MARGIN

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_p:
                    game.paused = not game.paused

                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move(-1)
                        game.move_repeat_dir = -1
                        game.move_repeat_timer = 0.0
                    elif event.key == pygame.K_RIGHT:
                        game.move(1)
                        game.move_repeat_dir = 1
                        game.move_repeat_timer = 0.0
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_DOWN:
                        game.soft_drop = True
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

                if game.game_over and event.key == pygame.K_r:
                    game = Tetris()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and game.move_repeat_dir == -1:
                    game.move_repeat_dir = 0
                    game.move_repeat_timer = 0.0
                elif event.key == pygame.K_RIGHT and game.move_repeat_dir == 1:
                    game.move_repeat_dir = 0
                    game.move_repeat_timer = 0.0
                elif event.key == pygame.K_DOWN:
                    game.soft_drop = False

        # update
        if not game.paused and not game.game_over:
            # give soft drop some extra "manual" feel:
            if game.soft_drop:
                game.soft_drop_step()
            game.update(dt)

        # render background
        screen.fill(BG)
        ox, oy = field_origin()

        # field background
        field_rect = pygame.Rect(ox, oy, COLS * CELL, ROWS * CELL)
        pygame.draw.rect(screen, GRID_BG, field_rect, border_radius=8)

        # grid lines
        for x in range(COLS + 1):
            px = ox + x * CELL
            pygame.draw.line(screen, GRID_LINE, (px, oy), (px, oy + ROWS * CELL))
        for y in range(ROWS + 1):
            py = oy + y * CELL
            pygame.draw.line(screen, GRID_LINE, (ox, py), (ox + COLS * CELL, py))

        # draw settled blocks
        for y in range(ROWS):
            for x in range(COLS):
                c = game.grid[y][x]
                if c is not None:
                    draw_cell(screen, ox + x * CELL, oy + y * CELL, c, 255)

        # ghost piece
        if not game.game_over:
            gy = game.ghost_y()
            for bx, by in game.current.blocks(y=gy):
                if by >= 0:
                    draw_cell(screen, ox + bx * CELL, oy + by * CELL, game.current.color, 70)

        # current piece
        if not game.game_over:
            for bx, by in game.current.blocks():
                if by >= 0:
                    draw_cell(screen, ox + bx * CELL, oy + by * CELL, game.current.color, 255)

        # side panel
        px = COLS * CELL + 20
        py = TOP_MARGIN

        draw_text(screen, big, "TETRIS", px, py - 10, TEXT)
        draw_text(screen, font, f"Score: {game.score}", px, py + 45, TEXT)
        draw_text(screen, font, f"Lines:  {game.lines}", px, py + 75, TEXT)
        draw_text(screen, font, f"Level:  {game.level}", px, py + 105, TEXT)

        draw_text(screen, font, "Next:", px, py + 150, TEXT)

        # next piece preview (4x4)
        preview_x = px
        preview_y = py + 185
        pygame.draw.rect(screen, (25, 27, 32), (preview_x, preview_y, 4 * CELL, 4 * CELL), border_radius=8)

        np = game.next_piece
        for bx, by in np.blocks(x=0, y=0):
            # center it roughly
            cx = preview_x + (bx) * CELL
            cy = preview_y + (by) * CELL
            draw_cell(screen, cx, cy, np.color, 255)

        # help
        help_y = py + 340
        draw_text(screen, small, "Controls:", px, help_y, SUBTEXT)
        draw_text(screen, small, "←/→ move", px, help_y + 22, SUBTEXT)
        draw_text(screen, small, "↑ rotate", px, help_y + 44, SUBTEXT)
        draw_text(screen, small, "↓ soft drop", px, help_y + 66, SUBTEXT)
        draw_text(screen, small, "Space hard drop", px, help_y + 88, SUBTEXT)
        draw_text(screen, small, "P pause  |  R restart", px, help_y + 110, SUBTEXT)

        # overlays
        if game.paused:
            overlay = pygame.Surface((COLS * CELL, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (ox, oy))
            draw_text(screen, big, "PAUSED", ox + 70, oy + 260, (240, 240, 240))

        if game.game_over:
            overlay = pygame.Surface((COLS * CELL, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (ox, oy))
            draw_text(screen, big, "GAME OVER", ox + 35, oy + 230, (255, 210, 210))
            draw_text(screen, font, "Press R to restart", ox + 45, oy + 280, TEXT)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
