import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta
GRID_SIZE = 10
CELL_SIZE = 30
MARGIN = 5
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * MARGIN
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + (GRID_SIZE + 1) * MARGIN + 80
MINE_COUNT = 15

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Minesweeper:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        self.reset_game()
    
    def reset_game(self):
        # Inisialisasi grid
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Status game
        self.game_over = False
        self.game_won = False
        self.first_click = True
        
        # Statistik
        self.flags_used = 0
        
    def place_mines(self, first_click_row, first_click_col):
        """Tempatkan mine setelah klik pertama untuk menghindari langsung kalah"""
        mines_placed = 0
        while mines_placed < MINE_COUNT:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            
            # Jangan tempatkan mine di posisi klik pertama atau yang sudah ada mine
            if (row != first_click_row or col != first_click_col) and self.grid[row][col] != -1:
                self.grid[row][col] = -1  # -1 menandakan mine
                mines_placed += 1
        
        # Hitung angka untuk setiap sel
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] != -1:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                                if self.grid[nr][nc] == -1:
                                    count += 1
                    self.grid[row][col] = count
    
    def reveal_cell(self, row, col):
        """Buka sel dan sel kosong di sekitarnya"""
        if (row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE or 
            self.revealed[row][col] or self.flagged[row][col]):
            return
        
        self.revealed[row][col] = True
        
        # Jika sel kosong (0), buka sel di sekitarnya
        if self.grid[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self.reveal_cell(row + dr, col + dc)
    
    def handle_click(self, pos, right_click=False):
        if self.game_over or self.game_won:
            return
        
        # Hitung posisi grid
        col = (pos[0] - MARGIN) // (CELL_SIZE + MARGIN)
        row = (pos[1] - MARGIN) // (CELL_SIZE + MARGIN)
        
        if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
            return
        
        if right_click:
            # Toggle flag
            if not self.revealed[row][col]:
                if self.flagged[row][col]:
                    self.flagged[row][col] = False
                    self.flags_used -= 1
                elif self.flags_used < MINE_COUNT:
                    self.flagged[row][col] = True
                    self.flags_used += 1
        else:
            # Left click - reveal cell
            if self.flagged[row][col]:
                return
            
            # Jika ini klik pertama, tempatkan mine
            if self.first_click:
                self.place_mines(row, col)
                self.first_click = False
            
            # Jika mengklik mine
            if self.grid[row][col] == -1:
                self.game_over = True
                # Reveal semua mine
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.grid[r][c] == -1:
                            self.revealed[r][c] = True
            else:
                self.reveal_cell(row, col)
                self.check_win()
    
    def check_win(self):
        """Cek apakah pemain menang"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] != -1 and not self.revealed[row][col]:
                    return
        self.game_won = True
    
    def get_cell_color(self, row, col):
        """Dapatkan warna untuk angka berdasarkan nilai"""
        colors = {
            1: BLUE,
            2: GREEN,
            3: RED,
            4: (128, 0, 128),  # Purple
            5: (128, 0, 0),    # Maroon
            6: (0, 128, 128),  # Teal
            7: BLACK,
            8: GRAY
        }
        return colors.get(self.grid[row][col], BLACK)
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Gambar grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * (CELL_SIZE + MARGIN) + MARGIN
                y = row * (CELL_SIZE + MARGIN) + MARGIN
                
                # Tentukan warna sel
                if self.revealed[row][col]:
                    if self.grid[row][col] == -1:
                        color = RED
                    else:
                        color = LIGHT_GRAY
                else:
                    color = GRAY
                
                # Gambar sel
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
                
                # Gambar konten sel
                if self.revealed[row][col]:
                    if self.grid[row][col] == -1:
                        # Gambar mine
                        pygame.draw.circle(self.screen, BLACK, 
                                         (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 
                                         CELL_SIZE // 4)
                    elif self.grid[row][col] > 0:
                        # Gambar angka
                        text = self.font.render(str(self.grid[row][col]), True, 
                                              self.get_cell_color(row, col))
                        text_rect = text.get_rect(center=(x + CELL_SIZE // 2, 
                                                        y + CELL_SIZE // 2))
                        self.screen.blit(text, text_rect)
                
                # Gambar flag
                if self.flagged[row][col]:
                    flag_points = [
                        (x + 5, y + 5),
                        (x + CELL_SIZE - 5, y + 5),
                        (x + CELL_SIZE - 5, y + CELL_SIZE // 2),
                        (x + 5, y + CELL_SIZE - 5)
                    ]
                    pygame.draw.polygon(self.screen, YELLOW, flag_points)
        
        # Gambar status
        y_offset = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN + 10
        
        # Jumlah flag tersisa
        flags_left = MINE_COUNT - self.flags_used
        flag_text = f"Flags: {flags_left}"
        text_surface = self.font.render(flag_text, True, BLACK)
        self.screen.blit(text_surface, (10, y_offset))
        
        # Status game
        if self.game_over:
            status_text = "GAME OVER! Press R to restart"
            color = RED
        elif self.game_won:
            status_text = "YOU WIN! Press R to restart"
            color = GREEN
        else:
            status_text = "Left click: Reveal | Right click: Flag"
            color = BLACK
        
        text_surface = self.font.render(status_text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 30))
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                    elif event.button == 3:  # Right click
                        self.handle_click(event.pos, right_click=True)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self.reset_game()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()