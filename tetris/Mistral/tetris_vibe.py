#!/usr/bin/env python3
"""
Tetris in Python mit Pygame
Ein einfaches Tetris-Spiel
"""

import pygame
import random

# Initialisierung von Pygame
pygame.init()

# Farben definieren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino-Formen (I, J, L, O, S, T, Z)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Farben für die Tetrominos
COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

class TetrisGame:
    def __init__(self):
        # Spielfeldgröße
        self.width = 10
        self.height = 20
        self.cell_size = 30
        
        # Fenstergröße berechnen
        self.window_width = self.width * self.cell_size + 200  # + Platz für Infos
        self.window_height = self.height * self.cell_size
        
        # Fenster erstellen
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Tetris")
        
        # Spielfeld initialisieren
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Aktuelles Tetromino
        self.current_piece = None
        self.next_piece = None
        
        # Spielstatus
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        
        # Timer für Fallgeschwindigkeit
        self.fall_time = 0
        self.fall_speed = 0.5  # Sekunden pro Zelle
        
        # Neue Tetrominos generieren
        self.new_piece()
        self.new_piece()

    def new_piece(self):
        """Erstellt ein neues zufälliges Tetromino"""
        if self.next_piece is None:
            shape = random.choice(SHAPES)
            self.current_piece = Tetromino(self.width // 2 - 2, 0, shape)
            self.next_piece = Tetromino(self.width // 2 - 2, 0, random.choice(SHAPES))
        else:
            self.current_piece = self.next_piece
            self.next_piece = Tetromino(self.width // 2 - 2, 0, random.choice(SHAPES))
        
        # Überprüfen auf Game Over
        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        """Überprüft, ob das aktuelle Tetromino mit dem Spielfeld oder den Rändern kollidiert"""
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    # Position im Spielfeld berechnen
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    
                    # Überprüfen auf Spielfeldgrenzen
                    if x < 0 or x >= self.width or y >= self.height:
                        return True
                    
                    # Überprüfen auf Kollision mit bestehenden Blöcken
                    if y >= 0 and self.grid[y][x]:
                        return True
        return False

    def rotate(self):
        """Dreht das aktuelle Tetromino"""
        # Speichere die aktuelle Rotation für den Fall, dass die Rotation nicht möglich ist
        old_rotation = self.current_piece.rotation
        old_shape = self.current_piece.shape
        
        # Rotation durchführen
        self.current_piece.rotation = (self.current_piece.rotation + 1) % 4
        self.current_piece.shape = [list(row) for row in zip(*self.current_piece.shape[::-1])]
        
        # Wenn Kollision nach Rotation, zurücksetzen
        if self.check_collision():
            self.current_piece.rotation = old_rotation
            self.current_piece.shape = old_shape

    def move(self, dx, dy):
        """Bewegt das aktuelle Tetromino"""
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        if self.check_collision():
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        return True

    def lock_piece(self):
        """Friert das aktuelle Tetromino im Spielfeld ein"""
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    if y >= 0:  # Nur wenn innerhalb des Spielfelds
                        self.grid[y][x] = self.current_piece.color
        
        # Zeilen löschen
        self.clear_lines()
        
        # Neues Tetromino generieren
        self.new_piece()

    def clear_lines(self):
        """Löscht vollständige Zeilen und aktualisiert die Punkte"""
        lines_to_clear = []
        
        for i, row in enumerate(self.grid):
            if all(row):
                lines_to_clear.append(i)
        
        # Zeilen von unten nach oben löschen
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(self.width)])
        
        # Punkte berechnen
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [100, 300, 500, 800][min(len(lines_to_clear) - 1, 3)] * self.level
            
            # Level anpassen
            self.level = self.lines_cleared // 10 + 1
            
            # Fallgeschwindigkeit erhöhen
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

    def draw(self):
        """Zeichnet das Spielfeld und die Tetrominos"""
        self.window.fill(BLACK)
        
        # Spielfeld zeichnen
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.window,
                        self.grid[y][x],
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    )
                    pygame.draw.rect(
                        self.window,
                        WHITE,
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                        1
                    )
        
        # Aktuelles Tetromino zeichnen
        if self.current_piece:
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        x = (self.current_piece.x + j) * self.cell_size
                        y = (self.current_piece.y + i) * self.cell_size
                        pygame.draw.rect(
                            self.window,
                            self.current_piece.color,
                            (x, y, self.cell_size, self.cell_size)
                        )
                        pygame.draw.rect(
                            self.window,
                            WHITE,
                            (x, y, self.cell_size, self.cell_size),
                            1
                        )
        
        # Nächstes Tetromino zeichnen (Miniaturansicht)
        if self.next_piece:
            next_x = self.width * self.cell_size + 20
            next_y = 50
            
            font = pygame.font.SysFont(None, 30)
            text = font.render("Next:", True, WHITE)
            self.window.blit(text, (next_x, next_y - 30))
            
            for i, row in enumerate(self.next_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        x = next_x + j * 20
                        y = next_y + i * 20
                        pygame.draw.rect(
                            self.window,
                            self.next_piece.color,
                            (x, y, 20, 20)
                        )
                        pygame.draw.rect(
                            self.window,
                            WHITE,
                            (x, y, 20, 20),
                            1
                        )
        
        # Spielinformationen anzeigen
        font = pygame.font.SysFont(None, 30)
        
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.window.blit(score_text, (self.width * self.cell_size + 20, 150))
        
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        self.window.blit(level_text, (self.width * self.cell_size + 20, 190))
        
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.window.blit(lines_text, (self.width * self.cell_size + 20, 230))
        
        # Game Over anzeigen
        if self.game_over:
            font = pygame.font.SysFont(None, 50)
            game_over_text = font.render("GAME OVER", True, RED)
            self.window.blit(game_over_text, (self.width * self.cell_size // 2 - 100, 
                                           self.height * self.cell_size // 2 - 25))
        
        pygame.display.flip()

    def run(self):
        """Hauptspielschleife"""
        clock = pygame.time.Clock()
        
        while not self.game_over:
            # Zeitmanagement
            dt = clock.tick(60) / 1000.0  # Delta-Time in Sekunden
            self.fall_time += dt
            
            # Ereignisse verarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate()
                    elif event.key == pygame.K_SPACE:
                        # Sofortiges Fallen
                        while self.move(0, 1):
                            pass
                        self.lock_piece()
            
            # Automatisches Fallen
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if not self.move(0, 1):
                    self.lock_piece()
            
            # Zeichnen
            self.draw()
        
        # Game Over - auf Benutzer warten
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Spiel neu starten
                        self.__init__()
                        self.run()
                        waiting = False
                    elif event.key == pygame.K_q:
                        waiting = False
            
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()