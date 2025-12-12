import pygame
import random
import sys

# --- Config ---
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
PLAY_WIDTH = 10  # Anzahl Spalten
PLAY_HEIGHT = 20  # Anzahl Zeilen
BLOCK_SIZE = 20

TOP_MARGIN = 50
SIDE_MARGIN = (WINDOW_WIDTH - PLAY_WIDTH * BLOCK_SIZE) // 2

# Farben
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)

# Tetromino Farben
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
}

# Formen: jede Form hat mehrere Rotationszustände
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


class Piece:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.rotations = SHAPES[shape_key]
        self.rotation = 0
        # Startposition (ungefähr in der Mitte)
        self.x = PLAY_WIDTH // 2 - 2
        self.y = 0

    @property
    def blocks(self):
        """Gibt Liste der (x, y)-Positionen auf dem Grid zurück."""
        return [(self.x + cx, self.y + cy) for (cx, cy) in self.rotations[self.rotation]]

    def rotate(self, grid):
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % len(self.rotations)
        if not is_valid_position(grid, self):
            # Rotation zurücknehmen, falls Kollision
            self.rotation = old_rotation


def create_grid(locked_positions=None):
    if locked_positions is None:
        locked_positions = {}
    grid = [[BLACK for _ in range(PLAY_WIDTH)] for _ in range(PLAY_HEIGHT)]
    for (x, y), color in locked_positions.items():
        if y >= 0:
            grid[y][x] = color
    return grid


def is_valid_position(grid, piece):
    for x, y in piece.blocks:
        if x < 0 or x >= PLAY_WIDTH or y >= PLAY_HEIGHT:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True


def get_new_piece():
    shape_key = random.choice(list(SHAPES.keys()))
    return Piece(shape_key)


def add_piece_to_locked(piece, locked):
    for x, y in piece.blocks:
        if y < 0:
            continue
        locked[(x, y)] = COLORS[piece.shape_key]


def clear_lines(locked):
    lines_cleared = 0
    for y in range(PLAY_HEIGHT - 1, -1, -1):
        if all((x, y) in locked for x in range(PLAY_WIDTH)):
            lines_cleared += 1
            # vollständige Zeile löschen
            for x in range(PLAY_WIDTH):
                del locked[(x, y)]
            # alles darüber nach unten verschieben
            for (x2, y2) in sorted(list(locked.keys()), key=lambda pos: pos[1]):
                if y2 < y:
                    locked[(x2, y2 + 1)] = locked.pop((x2, y2))
    return lines_cleared


def draw_grid_lines(surface):
    for y in range(PLAY_HEIGHT):
        pygame.draw.line(surface, GRAY,
                         (SIDE_MARGIN, TOP_MARGIN + y * BLOCK_SIZE),
                         (SIDE_MARGIN + PLAY_WIDTH * BLOCK_SIZE, TOP_MARGIN + y * BLOCK_SIZE))
    for x in range(PLAY_WIDTH):
        pygame.draw.line(surface, GRAY,
                         (SIDE_MARGIN + x * BLOCK_SIZE, TOP_MARGIN),
                         (SIDE_MARGIN + x * BLOCK_SIZE, TOP_MARGIN + PLAY_HEIGHT * BLOCK_SIZE))


def draw_window(surface, grid, score, level):
    surface.fill((15, 15, 30))
    # Titel
    font = pygame.font.SysFont("consolas", 28)
    label = font.render("TETRIS", True, WHITE)
    surface.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2, 10))

    # Score / Level
    stats_font = pygame.font.SysFont("consolas", 18)
    score_label = stats_font.render(f"Score: {score}", True, WHITE)
    level_label = stats_font.render(f"Level: {level}", True, WHITE)
    surface.blit(score_label, (20, 10))
    surface.blit(level_label, (20, 30))

    # Spielfeld-Hintergrund
    pygame.draw.rect(surface, (10, 10, 10),
                     (SIDE_MARGIN, TOP_MARGIN, PLAY_WIDTH * BLOCK_SIZE, PLAY_HEIGHT * BLOCK_SIZE))

    # Blöcke zeichnen
    for y in range(PLAY_HEIGHT):
        for x in range(PLAY_WIDTH):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(
                    surface,
                    color,
                    (SIDE_MARGIN + x * BLOCK_SIZE,
                     TOP_MARGIN + y * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE)
                )
                # dünner Rand für 3D-Effekt
                pygame.draw.rect(
                    surface,
                    (20, 20, 20),
                    (SIDE_MARGIN + x * BLOCK_SIZE,
                     TOP_MARGIN + y * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE),
                    1
                )

    draw_grid_lines(surface)
    pygame.display.update()


def main():
    pygame.init()
    pygame.display.setCaption = pygame.display.set_caption("Tetris")
    pygame.display.set_caption("Tetris")
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    locked = {}
    grid = create_grid(locked)

    current_piece = get_new_piece()
    next_drop_time = 0
    score = 0
    level = 1
    fall_speed = 500  # Millisekunden bis zum Fallen um eine Zeile

    running = True
    while running:
        dt = clock.tick(60)
        next_drop_time += dt

        # --- Eingaben ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not is_valid_position(grid, current_piece):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not is_valid_position(grid, current_piece):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    # Soft Drop
                    current_piece.y += 1
                    if not is_valid_position(grid, current_piece):
                        current_piece.y -= 1
                        # sofort festsetzen
                        add_piece_to_locked(current_piece, locked)
                        lines = clear_lines(locked)
                        if lines:
                            score += (100 * lines) * level
                        grid = create_grid(locked)
                        current_piece = get_new_piece()
                        if not is_valid_position(grid, current_piece):
                            # Game Over
                            running = False
                elif event.key in (pygame.K_UP, pygame.K_SPACE):
                    current_piece.rotate(grid)

        # --- Gravitation ---
        if next_drop_time > fall_speed:
            next_drop_time = 0
            current_piece.y += 1
            if not is_valid_position(grid, current_piece):
                current_piece.y -= 1
                add_piece_to_locked(current_piece, locked)
                lines = clear_lines(locked)
                if lines:
                    score += (100 * lines) * level
                    # Level-Up grob alle 1000 Punkte
                    level = 1 + score // 1000
                    fall_speed = max(100, 500 - (level - 1) * 30)
                grid = create_grid(locked)
                current_piece = get_new_piece()
                if not is_valid_position(grid, current_piece):
                    running = False

        # Grid mit aktueller Figur
        grid = create_grid(locked)
        for x, y in current_piece.blocks:
            if y >= 0:
                grid[y][x] = COLORS[current_piece.shape_key]

        draw_window(surface, grid, score, level)

    # Game Over Screen
    font = pygame.font.SysFont("consolas", 32)
    surface.fill((0, 0, 0))
    label = font.render("Game Over", True, WHITE)
    surface.blit(label, (WINDOW_WIDTH // 2 - label.get_width() // 2,
                         WINDOW_HEIGHT // 2 - label.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
