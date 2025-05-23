import pygame
import random

# Инициализация Pygame
pygame.init()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - голубой
    (0, 0, 255),  # J - синий
    (255, 165, 0),  # L - оранжевый
    (255, 255, 0),  # O - желтый
    (0, 255, 0),  # S - зеленый
    (128, 0, 128),  # T - фиолетовый
    (255, 0, 0)  # Z - красный
]

# Настройки игры
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = CELL_SIZE

# Фигуры Тетриса (тетромино)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]  # Z
]


class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # Поворот фигуры на 90 градусов
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]

        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]

        return rotated

    def can_rotate(self, grid):
        rotated_shape = self.rotate()
        for y, row in enumerate(rotated_shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x
                    new_y = self.y + y
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                            new_y >= GRID_HEIGHT or
                            (new_y >= 0 and grid[new_y][new_x])):
                        return False
        return True

    def perform_rotate(self):
        self.shape = self.rotate()

    def can_move(self, grid, dx, dy):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                            new_y >= GRID_HEIGHT or
                            (new_y >= 0 and grid[new_y][new_x])):
                        return False
        return True

    def move(self, grid, dx, dy):
        if self.can_move(grid, dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def draw(self, screen):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (self.x + x) * CELL_SIZE + GAME_AREA_LEFT,
                        (self.y + y) * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(screen, self.color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Тетрис')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # секунды между падением
        self.fall_time = 0

    def draw_grid(self):
        # Рисуем игровое поле
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * CELL_SIZE + GAME_AREA_LEFT,
                    y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, COLORS[self.grid[y][x] - 1], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Рисуем границы игровой области
        border_rect = pygame.Rect(
            GAME_AREA_LEFT,
            0,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)

        # Рисуем следующую фигуру
        next_text = self.font.render("Следующая:", True, WHITE)
        self.screen.blit(next_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 10, 30))

        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30 + x * CELL_SIZE,
                        80 + y * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Рисуем счет и уровень
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.level}", True, WHITE)
        self.screen.blit(score_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 10, 180))
        self.screen.blit(level_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 10, 220))

        if self.game_over:
            game_over_text = self.font.render("Игра Окончена!", True, (255, 0, 0))
            restart_text = self.font.render("Нажмите R для рестарта", True, WHITE)
            self.screen.blit(game_over_text, (GAME_AREA_LEFT + 30, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text, (GAME_AREA_LEFT + 10, SCREEN_HEIGHT // 2 + 10))

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.shape_idx + 1

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)

        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += (lines_cleared ** 2) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])

            self.grid = new_grid

    def check_collision(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell and (self.current_piece.y + y >= GRID_HEIGHT or
                             (self.current_piece.y + y >= 0 and
                              self.grid[self.current_piece.y + y][self.current_piece.x + x])):
                    return True
        return False

    def update(self, dt):
        if self.game_over:
            return

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.current_piece.move(self.grid, 0, 1):
                self.merge_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = Tetromino()
                if self.check_collision():
                    self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_LEFT:
                        self.current_piece.move(self.grid, -1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece.move(self.grid, 1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.current_piece.move(self.grid, 0, 1)
                    elif event.key == pygame.K_UP:
                        if self.current_piece.can_rotate(self.grid):
                            self.current_piece.perform_rotate()
                    elif event.key == pygame.K_SPACE:
                        while self.current_piece.move(self.grid, 0, 1):
                            pass
        return True

    def run(self):
        running = True
        last_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # в секундах
            last_time = current_time

            running = self.handle_events()

            self.screen.fill(BLACK)
            self.update(dt)
            self.draw_grid()
            self.current_piece.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()