import pygame
import sys
import random


# ========== CHANGE THESE DURING THE DEMO ==========

HUMAN_SHAPE = "x"                # "x", "o", "square", "triangle"
HUMAN_COLOR = (232, 90, 79)      # Red/coral

AI_SHAPE = "o"
AI_COLOR = (79, 168, 232)        # Blue

AI_GOES_FIRST = False

GRID_SIZE = 3                    # 3, 4, 5... just works

COLOR_BACKGROUND = (30, 30, 30)
COLOR_GRID = (80, 80, 80)


# ========== DEFAULT SETTINGS ==========

WINDOW_WIDTH = 600
LINE_WIDTH = 6
SYMBOL_WIDTH = 8
SYMBOL_PADDING = 30
FONT_SIZE = 40
COLOR_TEXT = (220, 220, 220)
COLOR_WIN_LINE = (255, 215, 0)

# Derived values
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE
STATUS_HEIGHT = 80
WINDOW_HEIGHT = WINDOW_WIDTH + STATUS_HEIGHT


# ========== GAME STATE ==========

board = []
current_turn = "human"
winner = None
winning_cells = None


def reset_board():
    global board, current_turn, winner, winning_cells
    board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    current_turn = "ai" if AI_GOES_FIRST else "human"
    winner = None
    winning_cells = None


# ========== BOARD LOGIC ==========

def get_empty_cells():
    cells = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] is None:
                cells.append((row, col))
    return cells


def check_winner():
    global winner, winning_cells

    # Check rows
    for row in range(GRID_SIZE):
        first = board[row][0]
        if first and all(board[row][col] == first for col in range(GRID_SIZE)):
            winner = first
            winning_cells = [(row, col) for col in range(GRID_SIZE)]
            return

    # Check columns
    for col in range(GRID_SIZE):
        first = board[0][col]
        if first and all(board[row][col] == first for row in range(GRID_SIZE)):
            winner = first
            winning_cells = [(row, col) for row in range(GRID_SIZE)]
            return

    # Check main diagonal
    first = board[0][0]
    if first and all(board[i][i] == first for i in range(GRID_SIZE)):
        winner = first
        winning_cells = [(i, i) for i in range(GRID_SIZE)]
        return

    # Check anti-diagonal
    first = board[0][GRID_SIZE - 1]
    if first and all(board[i][GRID_SIZE - 1 - i] == first for i in range(GRID_SIZE)):
        winner = first
        winning_cells = [(i, GRID_SIZE - 1 - i) for i in range(GRID_SIZE)]
        return

    # Check draw
    if not get_empty_cells():
        winner = "draw"


def make_move(row, col, player):
    global current_turn
    if board[row][col] is not None:
        return False
    board[row][col] = player
    check_winner()
    if winner is None:
        current_turn = "ai" if player == "human" else "human"
    return True


# ========== AI ==========

def ai_turn():
    empty = get_empty_cells()
    if empty:
        row, col = random.choice(empty)
        make_move(row, col, "ai")


# ========== DRAWING ==========

def draw_board(screen):
    for i in range(1, GRID_SIZE):
        # Horizontal lines
        y = STATUS_HEIGHT + i * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y), LINE_WIDTH)
        # Vertical lines
        x = i * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID, (x, STATUS_HEIGHT), (x, WINDOW_HEIGHT), LINE_WIDTH)


def draw_shape(screen, shape, color, row, col):
    x = col * CELL_SIZE
    y = STATUS_HEIGHT + row * CELL_SIZE
    pad = SYMBOL_PADDING

    if shape == "x":
        pygame.draw.line(screen, color, (x + pad, y + pad), (x + CELL_SIZE - pad, y + CELL_SIZE - pad), SYMBOL_WIDTH)
        pygame.draw.line(screen, color, (x + CELL_SIZE - pad, y + pad), (x + pad, y + CELL_SIZE - pad), SYMBOL_WIDTH)
    elif shape == "o":
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - pad
        pygame.draw.circle(screen, color, center, radius, SYMBOL_WIDTH)
    elif shape == "square":
        rect = pygame.Rect(x + pad, y + pad, CELL_SIZE - 2 * pad, CELL_SIZE - 2 * pad)
        pygame.draw.rect(screen, color, rect, SYMBOL_WIDTH)
    elif shape == "triangle":
        top = (x + CELL_SIZE // 2, y + pad)
        bottom_left = (x + pad, y + CELL_SIZE - pad)
        bottom_right = (x + CELL_SIZE - pad, y + CELL_SIZE - pad)
        pygame.draw.polygon(screen, color, [top, bottom_left, bottom_right], SYMBOL_WIDTH)


def draw_all_symbols(screen):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = board[row][col]
            if cell == "human":
                draw_shape(screen, HUMAN_SHAPE, HUMAN_COLOR, row, col)
            elif cell == "ai":
                draw_shape(screen, AI_SHAPE, AI_COLOR, row, col)


def draw_win_line(screen, cells):
    start_row, start_col = cells[0]
    end_row, end_col = cells[-1]
    start_x = start_col * CELL_SIZE + CELL_SIZE // 2
    start_y = STATUS_HEIGHT + start_row * CELL_SIZE + CELL_SIZE // 2
    end_x = end_col * CELL_SIZE + CELL_SIZE // 2
    end_y = STATUS_HEIGHT + end_row * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.line(screen, COLOR_WIN_LINE, (start_x, start_y), (end_x, end_y), SYMBOL_WIDTH + 4)


def draw_status(screen, font):
    if winner == "human":
        text = "You win!"
    elif winner == "ai":
        text = "AI wins!"
    elif winner == "draw":
        text = "Draw!"
    elif current_turn == "human":
        text = f"Your turn ({HUMAN_SHAPE})"
    else:
        text = f"AI turn ({AI_SHAPE})"

    surface = font.render(text, True, COLOR_TEXT)
    rect = surface.get_rect(center=(WINDOW_WIDTH // 2, STATUS_HEIGHT // 2))
    screen.blit(surface, rect)

    if winner:
        hint = font.render("Press R to restart", True, COLOR_TEXT)
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(hint, hint_rect)


# ========== MAIN ==========

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tic Tac Toe")
    font = pygame.font.Font(None, FONT_SIZE)
    clock = pygame.time.Clock()

    reset_board()

    # If AI goes first, make the first move
    if AI_GOES_FIRST:
        ai_turn()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_board()
                if AI_GOES_FIRST:
                    ai_turn()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if winner is None and current_turn == "human":
                    mouse_x, mouse_y = event.pos
                    if mouse_y > STATUS_HEIGHT:
                        col = mouse_x // CELL_SIZE
                        row = (mouse_y - STATUS_HEIGHT) // CELL_SIZE
                        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                            if make_move(row, col, "human"):
                                if winner is None:
                                    ai_turn()

        # Draw everything
        screen.fill(COLOR_BACKGROUND)
        draw_board(screen)
        draw_all_symbols(screen)
        if winning_cells:
            draw_win_line(screen, winning_cells)
        draw_status(screen, font)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
