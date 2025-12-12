import pygame, random

pygame.init()

# Fenster
WIDTH, HEIGHT = 300, 600
BLOCK = 30
COLS, ROWS = WIDTH // BLOCK, HEIGHT // BLOCK
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris in Python")

# Farben
COLORS = [
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0)
]

# Tetris-Formen (Matrizen)
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0],
     [1, 1, 1]],
    [[0, 0, 1],
     [1, 1, 1]],
    [[1, 1],
     [1, 1]],
    [[0, 1, 1],
     [1, 1, 0]],
    [[0, 1, 0],
     [1, 1, 1]],
    [[1, 1, 0],
     [0, 1, 1]]
]

# Spielfeld
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))


def valid_position(piece, adj_x=0, adj_y=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + adj_x
                new_y = piece.y + y + adj_y

                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False

                if new_y >= 0 and grid[new_y][new_x]:
                    return False
    return True


def place_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[piece.y + y][piece.x + x] = piece.color


def clear_lines():
    global grid
    new_grid = [row for row in grid if any(col == 0 for col in row)]
    cleared = ROWS - len(new_grid)
    grid = [[0 for _ in range(COLS)] for _ in range(cleared)] + new_grid


def draw_window():
    win.fill((0, 0, 0))

    # Grid zeichnen
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] != 0:
                pygame.draw.rect(win, grid[y][x],
                                 (x * BLOCK, y * BLOCK, BLOCK, BLOCK))

    pygame.display.update()


def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(win, piece.color,
                                 ((piece.x + x) * BLOCK,
                                  (piece.y + y) * BLOCK,
                                  BLOCK, BLOCK))


def main():
    run = True
    clock = pygame.time.Clock()
    fall_time = 0

    piece = Piece()

    while run:
        dt = clock.tick(60)
        fall_time += dt

        # Automatisches Fallen
        if fall_time > 500:
            if valid_position(piece, 0, 1):
                piece.y += 1
            else:
                place_piece(piece)
                clear_lines()
                piece = Piece()

                if not valid_position(piece):
                    print("Game Over")
                    run = False

            fall_time = 0

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and valid_position(piece, -1, 0):
            piece.x -= 1
        if keys[pygame.K_RIGHT] and valid_position(piece, 1, 0):
            piece.x += 1
        if keys[pygame.K_DOWN] and valid_position(piece, 0, 1):
            piece.y += 1
        if keys[pygame.K_UP]:
            old_shape = piece.shape
            piece.rotate()
            if not valid_position(piece):
                piece.shape = old_shape
        if keys[pygame.K_SPACE]:
            while valid_position(piece, 0, 1):
                piece.y += 1
            place_piece(piece)
            clear_lines()
            piece = Piece()

        # Zeichnen
        draw_window()
        draw_piece(piece)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
