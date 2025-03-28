import pygame
import Sudoku
import numpy as np

pygame.init()
pygame.font.init()

RED, GREEN, BLUE = "#e63946", (0, 240, 0), "#023e8a"
BACKGROUND_COLOR = "#faedcd"
TEXT_COLOR = "#415a77"
TILE_GAP_COLOR = "#d4a373"
NUMBER_COLOR = "#778da9"
BUTTON_COLOR = "#e9edc9"
BUTTON_HOVERED_COLOR = "#ccd5ae"
BUTTON_BORDER_COLOR = "#adc178"
BUTTON_TEXT_COLOR = "#588157"

WINDOW_HEIGHT, WINDOW_WIDTH = 700, 700
TEXT_FONT = pygame.font.Font("Chalkboard.ttc", size = 50)
NUMBER_FONT = pygame.font.Font("Chalkboard.ttc", size = 33)
BUTTON_FONT = pygame.font.Font("Chalkboard.ttc", size = 20)

class Button:
    """
    Represent a button in game display
    """
    def __init__(self, x: int, y: int, text: str, width: int, height: int):
        """
        Initialize a button. Create a text surface, text rectangle from the given text.
        Create a rectangle for the button and place the text in the middle of the button
        :param x: top left position of button
        :param y: top left position of button
        :param text: text on the button
        :param width: width of the button
        :param height: height of the button
        """
        self.text_surface = BUTTON_FONT.render(text, True, BUTTON_TEXT_COLOR)
        self.text_rect = self.text_surface.get_rect()
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.text_rect.center = self.rect.center
        self.clicked = False

    def draw(self, window: pygame.Surface, is_hovered: bool):
        """
        Draw the button on the game window
        :param window: the game window
        :param is_hovered: if the mouse curser is hovered on the button
        """
        color = BUTTON_COLOR if not is_hovered else BUTTON_HOVERED_COLOR
        pygame.draw.rect(window, color, self.rect, border_radius = 8)
        pygame.draw.rect(window, BUTTON_BORDER_COLOR, self.rect, 2, 8)
        window.blit(self.text_surface, self.text_rect)

    def is_hover(self) -> bool:
        """
        If the mouse curser is on the button
        :return: True if the mouse curser is on the button
        """
        mouse = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse)

    def is_clicked(self) -> bool:
        """
        Check if the button is clicked
        :return: True if the button is clicked
        """
        if self.is_hover():
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                return True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        return False

class Tile:
    """
    Represent a square on the sudoku board.
    Each square belongs to exactly one grid
    """
    TILE_WIDTH = 50
    TILE_GAP = 8

    def __init__(self, grid: 'Grid', x: int, y: int, rect: pygame.Rect, current_number: int, expected_number : int):
        """
        Initialize a tile
        :param grid: the grid of the tile
        :param x: the top left position of the tile
        :param y: the top left position of the tile
        :param rect: the rectangle of the tile on the grid
        :param current_number: the current number of the tile (0 to 9)
        :param expected_number: the number of this position on the solution board
        """
        self.grid = grid
        self.x = x
        self.y = y
        self.rect = rect
        self.current_number = current_number
        self.expected_number = expected_number

    def place_number(self, window: pygame.Surface, solution: bool):
        """
        Place the number in the middle of the rectangle of this tile
        :param window: the game window
        :param solution: if the current or expected number should be placed
        """
        if not solution:
            num = NUMBER_FONT.render(str(self.current_number) if self.current_number != 0 else "", True, NUMBER_COLOR)
        else:
            num = NUMBER_FONT.render(str(self.expected_number), True, NUMBER_COLOR)
            self.current_number = self.expected_number
        num_rect = num.get_rect()
        num_rect.center = self.rect.center
        window.blit(num, num_rect)

    def change_number(self,window: pygame.Surface, number: int):
        """
        Change the number accordingly to the user's input
        :param window: the game window
        :param number: the number the user typed in
        """
        self.current_number = number
        pygame.draw.rect(window, BACKGROUND_COLOR, self.rect)
        pygame.draw.rect(window, TILE_GAP_COLOR, self.rect, 2)
        self.place_number(window, False)
        self.grid.check_number(self)

    def is_clicked(self, window: pygame.Surface) -> ('Tile', bool):
        """
        Check if this tile is clicked.
        Highlight the tile with blue if the tile is clicked, red if the current number is not the expected one
        :param window: the game window
        :return: (self, True) if this tile is clicked or (None, False) otherwise
        """
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse) and self.current_number != self.expected_number:
            pygame.draw.rect(window, BLUE, self.rect, 1)
            return self, True
        elif self.current_number != 0 and self.current_number != self.expected_number:
            pygame.draw.rect(window, RED, self.rect, 1)
            return None, False
        else:
            pygame.draw.rect(window, TILE_GAP_COLOR, self.rect, 1)
            return None, False

class Grid:
    """
    Represent the game board.
    A game board contains of 81 tiles
    """
    START_POSITION = 120

    def __init__(self, window: pygame.Surface, pre_solved: np.ndarray):
        """
        Initialize the game board. Generate a game board and the corresponding solution.
        Create an array to store all the tiles
        :param window: the game window
        :param pre_solved: a pre-solved game board to generate a new one from
        """
        self.board, self.solution = Sudoku.generate(pre_solved.copy(), 9, 30)
        self.pre_solved = pre_solved
        self.window = window
        self.tiles = np.empty((9, 9), dtype = object)

    def init_grid(self):
        """
        Create a tile for each square of the game board and store them in an array
        :return:
        """
        x, y = Grid.START_POSITION, Grid.START_POSITION
        w = Tile.TILE_WIDTH
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                rect = pygame.Rect(x, y, w, w)
                pygame.draw.rect(self.window, TILE_GAP_COLOR, rect, 2)
                tile = Tile(self, x, y, rect, self.board[row, col], self.solution[row, col])
                tile.place_number(self.window, False)
                self.tiles[row, col] = tile
                x = x + w
                if col % 3 == 2:
                    x += Tile.TILE_GAP
            y = y + w
            if row % 3 == 2:
                y += Tile.TILE_GAP
            x = Grid.START_POSITION

    def is_clicked(self) -> Tile:
        """
        Find out which tile is clicked
        :return: the clicked tile
        """
        chosen_tile = None
        for row in self.tiles:
            for tile in row:
                clicked_tile, clicked = tile.is_clicked(self.window)
                if clicked:
                    chosen_tile = clicked_tile
        return chosen_tile

    def check_number(self, tile: Tile):
        """
        Check if the current number is valid or not. If not, highlight all the conflicted tiles with red
        :param tile: the tile to check for validation
        """
        if tile.current_number != 0:
            pos = np.argwhere(self.tiles == tile).flatten()
            valid, conflicts = Sudoku.is_valid_value(self.board, tuple(pos), tile.current_number)
            pygame.draw.rect(self.window, GREEN if valid else RED, tile.rect, 1)
            for pos in conflicts:
                pygame.draw.rect(self.window, RED, self.tiles[pos], 1)
        else:
            for row in self.tiles:
                for tile in row:
                    pygame.draw.rect(self.window, TILE_GAP_COLOR, tile.rect, 1)

    def show_solution(self):
        """
        Display the solution for this game board
        """
        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                tile = self.tiles[row, col]
                if tile.current_number != tile.expected_number:
                    pygame.draw.rect(self.window, BACKGROUND_COLOR, tile.rect)
                    tile.place_number(self.window, True)
                    pygame.draw.rect(self.window, GREEN, tile.rect, 1)

    def show_hint(self):
        """
        Choose a random unassigned or wrong tile and display the correct solution for this tile
        """
        unassigned = [tile for tile in self.tiles.flatten() if tile.current_number != tile.expected_number]
        if len(unassigned) != 0:
            rand = np.random.choice(unassigned)
            rand.place_number(self.window, True)
            pygame.draw.rect(self.window, GREEN, rand.rect, 1)

    def reset(self):
        """
        Reset the game board by creating a new game board and solution. Display the new board
        """
        self.board, self.solution = Sudoku.generate(self.pre_solved.copy(), 9, 30)
        self.tiles = np.empty((9, 9), dtype = object)
        self.window.fill(BACKGROUND_COLOR)
        text = TEXT_FONT.render("Let's play SUDOKU!", True, TEXT_COLOR)
        self.window.blit(text, (130, 30))
        self.init_grid()

def init_window() -> (Grid, pygame.Surface):
    """
    Initialize the game window
    :return: the grid and window of the game
    """
    pygame.display.set_caption("Mudomu")

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    window.fill(BACKGROUND_COLOR)

    text = TEXT_FONT.render("Let's play SUDOKU!", True, TEXT_COLOR)
    window.blit(text, (130, 30))

    grid = Grid(window, Sudoku.pre_solved)
    grid.init_grid()

    return grid, window

def main():
    """
    The main starting point.
    Control the flow of the game
    """
    grid, window = init_window()
    tile = None

    buttons = {
        "solve" : Button(580, 620,"Solve", 70, 40),
        "hint" : Button(500, 620, "Hint", 70, 40),
        "again" : Button(420, 620, "Again", 70, 40)
    }
    for button in buttons.values():
        button.draw(window, False)

    running = True
    while running:
        for b in buttons.values():
            if b.is_hover():
                b.draw(window, True)
            else:
                b.draw(window, False)
        if buttons.get("solve").is_clicked():
            grid.show_solution()
        if buttons.get("hint").is_clicked():
            grid.show_hint()
        if buttons.get("again").is_clicked():
            grid.reset()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                tile = grid.is_clicked()
            elif e.type == pygame.KEYDOWN and tile is not None:
                if e.key == pygame.K_BACKSPACE:
                    tile.change_number(window, 0)
                elif e.unicode.isdigit():
                    tile.change_number(window, 0)
                    tile.change_number(window, int(e.unicode))

        pygame.display.update()

main()
pygame.quit()