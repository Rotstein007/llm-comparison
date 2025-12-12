import pygame
import random
from dataclasses import dataclass

# -----------------------------
# Config
# -----------------------------
CELL = 30
COLS = 10
ROWS = 20

PLAY_W = COLS * CELL
PLAY_H = ROWS * CELL
SIDE_W = 220
W = PLAY_W + SIDE_W
H = PLAY_H

FPS = 60

# Fallgeschwindigkeit (Zellen pro Sekunde)
BASE_FALL_SPEED = 1.0

# Farben
BG = (18, 18, 22)
GRID = (40, 40, 55)
TEXT = (230, 230, 240)

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 120, 240),
    "L": (240, 160, 0),
}

# 4x4 Patterns (Rotation wird berechnet)
SHAPES = {
    "I": [
        "....",
        "####",
        "....",
        "....",
    ],
    "O": [
        ".##.",
        ".##.",
        "....",
        "....",
    ],
    "T": [
        ".#..",
        "###.",
        "....",
        "....",
    ],
    "S": [
        ".##.",
        "##..",
        "....",
        "....",
    ],
    "Z": [
        "##..",
        ".##.",
        "....",
        "....",
    ],
    "J": [
        "#...",
        "###.",
        "....",
        "....",
    ],
    "L": [
        "..#.",
        "###.",
        "....",
        "....",
    ],
}


def rotate_4x4(pattern):
    """Rotate 4x4 pattern clockwise."""
    grid = [list(row) for row in pattern]
    rotated = list(zip(*grid[::-1]))
    return ["".join(r) for r in rotated]


def pattern_cells(pattern):
    """Return list of (x,y) for '#' in 4x4 pattern."""
    cells = []
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == "#":
                cells.append((x, y))
    return cells


@dataclass
class Piece:
    kind: str
    x: int
    y: int
    rot: int = 0

    @property
    def color(self):
        return COLORS[self.kind]

    def patterns(self):
        p = SHAPES[self.kind]
        for _ in range(self.rot % 4):
            p = rotate_4x4(p)
        return p

    def cells(self):
        return [(self.x + cx, self.y + cy) for (cx, cy) in pattern_cells(self.patterns())]


class Bag7:
    def __init__(self):
        self.bag = []

    def next(self):
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()


class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.bag = Bag7()
        self.next_kind = self.bag.next()
        self.piece = self.spawn_piece()
        self.hold_kind = None
        self.hold_used = False

        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False

        self.drop_acc = 0.0

    def spawn_piece(self):
        kind = self.next_kind
        self.next_kind = self.bag.next()

        # Spawn in middle, slightly above visible area
        p = Piece(kind=kind, x=COLS // 2 - 2, y=-1, rot=0)
        if not self.valid(p, dx=0, dy=0, drot=0):
            self.game_over = True
        self.hold_used = False
        return p

    def valid(self, piece, dx=0, dy=0, drot=0):
        test = Piece(piece.kind, piece.x + dx, piece.y + dy, (piece.rot + drot) % 4)
        for (x, y) in test.cells():
            if x < 0 or x >= COLS:
                return False
            if y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self):
        for (x, y) in self.piece.cells():
            if y >= 0:
                self.grid[y][x] = self.piece.kind
        cleared = self.clear_lines()
        self.apply_scoring(cleared)
        self.piece = self.spawn_piece()

    def hard_drop(self):
        dist = 0
        while self.valid(self.piece, dy=1):
            self.piece.y += 1
            dist += 1
        self.score += 2 * dist
        self.lock_piece()

    def soft_drop(self):
        if self.valid(self.piece, dy=1):
            self.piece.y += 1
            self.score += 1
        else:
            self.lock_piece()

    def move(self, dx):
        if self.valid(self.piece, dx=dx):
            self.piece.x += dx

    def rotate(self):
        # simple wall-kick set
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
        for kx, ky in kicks:
            if self.valid(self.piece, dx=kx, dy=ky, drot=1):
                self.piece.x += kx
                self.piece.y += ky
                self.piece.rot = (self.piece.rot + 1) % 4
                return

    def hold(self):
        if self.hold_used:
            return
        self.hold_used = True
        current = self.piece.kind
        if self.hold_kind is None:
            self.hold_kind = current
            self.piece = self.spawn_piece()
        else:
            self.piece = Piece(kind=self.hold_kind, x=COLS // 2 - 2, y=-1, rot=0)
            self.hold_kind = current
            if not self.valid(self.piece):
                self.game_over = True

    def clear_lines(self):
        new_grid = []
        cleared = 0
        for row in self.grid:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_grid.append(row)
        while len(new_grid) < ROWS:
            new_grid.insert(0, [None for _ in range(COLS)])
        self.grid = new_grid
        return cleared

    def apply_scoring(self, cleared):
        if cleared == 0:
            return
        # Classic-ish scoring
        points = {1: 100, 2: 300, 3: 500, 4: 800}[cleared]
        self.score += points * self.level
        self.lines += cleared
        self.level = 1 + self.lines // 10

    def fall_speed(self):
        # Level macht schneller (nicht zu extrem)
        return BASE_FALL_SPEED + 0.15 * (self.level - 1)

    def update(self, dt, fast_drop=False):
        if self.game_over:
            return
        speed = self.fall_speed() * (10 if fast_drop else 1)
        self.drop_acc += dt * speed
        while self.drop_acc >= 1.0:
            self.drop_acc -= 1.0
            if self.valid(self.piece, dy=1):
                self.piece.y += 1
            else:
                self.lock_piece()
                break


def draw_cell(screen, x, y, color):
    r = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
    pygame.draw.rect(screen, color, r)
    pygame.draw.rect(screen, (0, 0, 0), r, 1)


def draw_grid_lines(screen):
    for x in range(COLS + 1):
        pygame.draw.line(screen, GRID, (x * CELL, 0), (x * CELL, PLAY_H))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, GRID, (0, y * CELL), (PLAY_W, y * CELL))


def draw_piece(screen, piece):
    for (x, y) in piece.cells():
        if y >= 0:
            draw_cell(screen, x, y, piece.color)


def draw_board(screen, game):
    for y in range(ROWS):
        for x in range(COLS):
            kind = game.grid[y][x]
            if kind is not None:
                draw_cell(screen, x, y, COLORS[kind])


def mini_draw(screen, kind, ox, oy):
    # Draw 4x4 mini at offset (pixels)
    pat = SHAPES[kind]
    cells = pattern_cells(pat)
    for cx, cy in cells:
        r = pygame.Rect(ox + cx * (CELL // 2), oy + cy * (CELL // 2), CELL // 2, CELL // 2)
        pygame.draw.rect(screen, COLORS[kind], r)
        pygame.draw.rect(screen, (0, 0, 0), r, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Tetris (Python / pygame)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    small = pygame.font.SysFont("consolas", 18)

    game = Tetris()
    fast_drop = False

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

                if game.game_over:
                    if event.key == pygame.K_r:
                        game = Tetris()
                    continue

                if event.key == pygame.K_LEFT:
                    game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move(1)
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()
                elif event.key == pygame.K_c:
                    game.hold()
                elif event.key == pygame.K_DOWN:
                    fast_drop = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fast_drop = False

        game.update(dt, fast_drop=fast_drop)

        # Render
        screen.fill(BG)

        # Playfield
        draw_board(screen, game)
        if not game.game_over:
            draw_piece(screen, game.piece)
        draw_grid_lines(screen)

        # Side panel
        sx = PLAY_W + 16
        screen.blit(font.render("NEXT", True, TEXT), (sx, 16))
        mini_draw(screen, game.next_kind, sx, 48)

        screen.blit(font.render("HOLD", True, TEXT), (sx, 140))
        if game.hold_kind:
            mini_draw(screen, game.hold_kind, sx, 172)
        else:
            screen.blit(small.render("(press C)", True, (160, 160, 170)), (sx, 175))

        screen.blit(font.render(f"SCORE {game.score}", True, TEXT), (sx, 280))
        screen.blit(font.render(f"LINES {game.lines}", True, TEXT), (sx, 312))
        screen.blit(font.render(f"LEVEL {game.level}", True, TEXT), (sx, 344))

        # Help
        help_lines = [
            "←/→ Move",
            "↑ Rotate",
            "↓ Soft/Fast drop",
            "Space Hard drop",
            "C Hold",
            "R Restart (game over)",
            "Esc Quit",
        ]
        yy = 410
        screen.blit(font.render("CONTROLS", True, TEXT), (sx, yy))
        yy += 30
        for h in help_lines:
            screen.blit(small.render(h, True, (190, 190, 205)), (sx, yy))
            yy += 22

        if game.game_over:
            overlay = pygame.Surface((PLAY_W, PLAY_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            msg1 = font.render("GAME OVER", True, (255, 255, 255))
            msg2 = small.render("Press R to restart", True, (230, 230, 240))
            screen.blit(msg1, (PLAY_W // 2 - msg1.get_width() // 2, PLAY_H // 2 - 30))
            screen.blit(msg2, (PLAY_W // 2 - msg2.get_width() // 2, PLAY_H // 2 + 5))

        pygame.display.flip()


if __name__ == "__main__":
    main()
