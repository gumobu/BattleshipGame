import pygame


class Grid:
    """
    Class to draw the grids and add title, numbers and letters to them
    ----------
    Attributes:
        title (str): Players' name to be displayed on the top of his grid
        offset (int): Where the grid starts (in number of blocks)
                (typically 0 for computer and 15 for human)
        screen (pygame.screen): Surface to display everything on
        params (tuple): a tuple of variables, necessary for code running
    ----------
    Methods:
        __draw_grid(): Draws two grids for both players
        __add_nums_letters_to_grid(): Draws numbers 1-10 along vertical and adds letters below horizontal
            lines for both grids
        __sign_grid(): Puts players' names (titles) in the center above the grids
    """

    def __init__(self, title, offset, screen, params):
        """
        title(str): Players' name to be displayed on the top of his grid
        offset (int): Where the grid starts (in number of blocks)
        (typically 0 for computer and 15 for human)
        """
        self.title = title
        self.offset = offset
        self.screen = screen
        self.LETTERS, self.BLACK, self.left_margin, self.upper_margin, self.block_size, self.font, self.font_size =\
            params
        self.__draw_grid()
        self.__add_nums_letters_to_grid()
        self.__sign_grid()

    def __draw_grid(self):
        """
        Draws a grid for player
        """
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(self.screen, self.BLACK, (self.left_margin + self.offset * self.block_size,
                                                       self.upper_margin + i * self.block_size),
                             (self.left_margin + (10 + self.offset) * self.block_size,
                              self.upper_margin + i * self.block_size), 1)
            # Vertical lines
            pygame.draw.line(self.screen, self.BLACK, (self.left_margin + (i + self.offset) * self.block_size,
                                                       self.upper_margin),
                             (self.left_margin + (i + self.offset) * self.block_size,
                              self.upper_margin + 10 * self.block_size), 1)

    def __add_nums_letters_to_grid(self):
        """
        Draws numbers 1-10 along vertical and adds letters below horizontal
        lines for a grid
        """
        for i in range(10):
            num_ver = self.font.render(str(i + 1), True, self.BLACK)
            letters_hor = self.font.render(self.LETTERS[i], True, self.BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Numbers (vertical)
            self.screen.blit(num_ver, (self.left_margin - (self.block_size // 2 + num_ver_width // 2) +
                                       self.offset * self.block_size,
                                       self.upper_margin + i * self.block_size +
                                       (self.block_size // 2 - num_ver_height // 2)))
            # Letters (horizontal)
            self.screen.blit(letters_hor, (self.left_margin + i * self.block_size +
                                           (self.block_size // 2 - letters_hor_width // 2) +
                                           self.offset * self.block_size,
                                           self.upper_margin + 10 * self.block_size))

    def __sign_grid(self):
        """
        Puts player's name (title) in the center above the grid
        """
        player = self.font.render(self.title, True, self.BLACK)
        sign_width = player.get_width()
        self.screen.blit(player, (self.left_margin + 5 * self.block_size - sign_width // 2 +
                                  self.offset * self.block_size,
                         self.upper_margin - self.block_size // 2 - self.font_size))
