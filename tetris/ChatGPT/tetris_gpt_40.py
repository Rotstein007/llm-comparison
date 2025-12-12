import pygame
import random

# Initialisiere pygame
pygame.init()

# Bildschirmgröße
WIDTH, HEIGHT = 300, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Spielfeld-Größe in Blöcken
ROWS, COLS = 20, 10
BLOCK_SIZE = WIDTH // COLS

# Farben
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# Formen (Tetris-Blöcke)
SHAPES = [
    [[1, 1, 1, 1]],                          # I
    [[1, 0, 0], [1, 1, 1]],                  # J
    [[0, 0, 1], [1, 1, 1]],                  # L
    [[1, 1], [1, 1]],                        # O
    [[0, 1, 1], [1, 1, 0]],                  # S
    [[0, 1, 0], [1, 1, 1]],                  # T
    [[1, 1, 0], [0, 1, 1]]                   # Z
]

# Spielfeld initialisieren
def create_grid():
    return [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

# Aktueller Block
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def rotated_shape(self):
        return list(zip(*self.shape[::-1]))

# Zeichnet das Spielfeld
def draw_grid(win, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(win, grid[i][j],
                             (j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for i in range(ROWS):
        pygame.draw.line(win, GRAY, (0, i*BLOCK_SIZE), (WIDTH, i*BLOCK_SIZE))
    for j in range(COLS):
        pygame.draw.line(win, GRAY, (j*BLOCK_SIZE, 0), (j*BLOCK_SIZE, HEIGHT))

# Block zeichnen
def draw_piece(win, piece):
    shape = piece.shape
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    win,
                    piece.color,
                    ((piece.x + j) * BLOCK_SIZE,
                     (piece.y + i) * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE)
                )

# Kollision prüfen
def valid_space(piece, grid):
    shape = piece.shape
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                x = piece.x + j
                y = piece.y + i
                if x < 0 or x >= COLS or y >= ROWS:
                    return False
                if y >= 0 and grid[y][x] != BLACK:
                    return False
    return True

# Form auf dem Spielfeld fixieren
def lock_piece(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                grid[piece.y + i][piece.x + j] = piece.color

# Volle Reihen entfernen
def clear_rows(grid):
    new_grid = [row for row in grid if any(cell == BLACK for cell in row)]
    rows_cleared = ROWS - len(new_grid)
    for _ in range(rows_cleared):
        new_grid.insert(0, [BLACK for _ in range(COLS)])
    return new_grid

# Hauptspiel
def main():
    grid = create_grid()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    current_piece = Piece(3, 0, random.choice(SHAPES))
    run = True

    while run:
        grid = clear_rows(grid)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                lock_piece(current_piece, grid)
                current_piece = Piece(3, 0, random.choice(SHAPES))
                if not valid_space(current_piece, grid):
                    print("GAME OVER")
                    run = False
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.shape = list(zip(*current_piece.shape[::-1]))
                    if not valid_space(current_piece, grid):
                        current_piece.shape = list(zip(*current_piece.shape))[::-1]

        win.fill(BLACK)
        draw_grid(win, grid)
        draw_piece(win, current_piece)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
