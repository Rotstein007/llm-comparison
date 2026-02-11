import tkinter as tk
import random
from typing import List, Optional


class Tetris:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Tetris")
        self.master.resizable(False, False)

        self.CELL_SIZE = 30
        self.GRID_WIDTH = 10
        self.GRID_HEIGHT = 20

        self.colors = [
            "#00FFFF",  # Cyan (I)
            "#FFFF00",  # Yellow (O)
            "#800080",  # Purple (T)
            "#00FF00",  # Green (S)
            "#FF0000",  # Red (Z)
            "#0000FF",  # Blue (J)
            "#FFA500",  # Orange (L)
        ]

        self.shapes: List[List[List[int]]] = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[0, 1, 0], [1, 1, 1]],
            [[0, 1, 1], [1, 1, 0]],
            [[1, 1, 0], [0, 1, 1]],
            [[1, 0, 0], [1, 1, 1]],
            [[0, 0, 1], [1, 1, 1]],
        ]

        self.canvas = tk.Canvas(
            master,
            width=self.CELL_SIZE * self.GRID_WIDTH,
            height=self.CELL_SIZE * self.GRID_HEIGHT,
            bg="black",
        )
        self.canvas.pack(side=tk.LEFT)

        self.info_frame = tk.Frame(master)
        self.info_frame.pack(side=tk.RIGHT, padx=10)

        self.score_label = tk.Label(
            self.info_frame, text="Score: 0", font=("Arial", 14)
        )
        self.score_label.pack()

        self.game_over_label = tk.Label(
            self.info_frame, text="", font=("Arial", 14), fg="red"
        )
        self.game_over_label.pack()

        self.restart_button = tk.Button(
            self.info_frame, text="Restart", command=self.restart
        )
        self.restart_button.pack(pady=10)

        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)
        ]
        self.score = 0
        self.game_over = False
        self.current_x = 0
        self.current_y = 0
        self.current_shape: List[List[int]] = []
        self.current_color = ""

        self.master.bind("<Left>", lambda e: self.move(-1, 0))
        self.master.bind("<Right>", lambda e: self.move(1, 0))
        self.master.bind("<Down>", lambda e: self.move(0, 1))
        self.master.bind("<Up>", lambda e: self.rotate())
        self.master.bind("<space>", lambda e: self.hard_drop())

        self.restart()

    def restart(self):
        self.canvas.delete("all")
        self.grid = [
            [None for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)
        ]
        self.score = 0
        self.game_over = False
        self.score_label.config(text="Score: 0")
        self.game_over_label.config(text="")
        self.spawn_piece()
        self.game_loop()

    def spawn_piece(self):
        shape_idx = random.randint(0, 6)
        self.current_shape = [row[:] for row in self.shapes[shape_idx]]
        self.current_color = self.colors[shape_idx]
        self.current_x = self.GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        if self.check_collision(self.current_x, self.current_y, self.current_shape):
            self.game_over = True
            self.game_over_label.config(text="GAME OVER")

    def check_collision(self, x: int, y: int, shape: List[List[int]]) -> bool:
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if (
                        new_x < 0
                        or new_x >= self.GRID_WIDTH
                        or new_y >= self.GRID_HEIGHT
                        or (new_y >= 0 and self.grid[new_y][new_x] is not None)
                    ):
                        return True
        return False

    def lock_piece(self):
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = self.current_x + col_idx
                    y = self.current_y + row_idx
                    if y >= 0:
                        self.grid[y][x] = self.current_color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        lines_cleared = 0
        y = self.GRID_HEIGHT - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        self.score += lines_cleared * 100
        self.score_label.config(text=f"Score: {self.score}")

    def move(self, dx: int, dy: int):
        if self.game_over:
            return
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if not self.check_collision(new_x, new_y, self.current_shape):
            self.current_x = new_x
            self.current_y = new_y
            if dy > 0:
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")
            self.draw()
        elif dy > 0:
            self.lock_piece()

    def rotate(self):
        if self.game_over:
            return
        rotated = [list(row) for row in zip(*self.current_shape[::-1])]
        if not self.check_collision(self.current_x, self.current_y, rotated):
            self.current_shape = rotated
            self.draw()

    def hard_drop(self):
        if self.game_over:
            return
        while not self.check_collision(
            self.current_x, self.current_y + 1, self.current_shape
        ):
            self.current_y += 1
            self.score += 2
        self.score_label.config(text=f"Score: {self.score}")
        self.lock_piece()
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        # Draw locked pieces
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color is not None:
                    self.canvas.create_rectangle(
                        x * self.CELL_SIZE,
                        y * self.CELL_SIZE,
                        (x + 1) * self.CELL_SIZE,
                        (y + 1) * self.CELL_SIZE,
                        fill=color,
                        outline="gray",
                    )

        # Draw current piece
        for y, row in enumerate(self.current_shape):
            for x, cell in enumerate(row):
                if cell:
                    self.canvas.create_rectangle(
                        (self.current_x + x) * self.CELL_SIZE,
                        (self.current_y + y) * self.CELL_SIZE,
                        (self.current_x + x + 1) * self.CELL_SIZE,
                        (self.current_y + y + 1) * self.CELL_SIZE,
                        fill=self.current_color,
                        outline="gray",
                    )

    def game_loop(self):
        if not self.game_over:
            self.move(0, 1)
            self.draw()
            self.master.after(500, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
