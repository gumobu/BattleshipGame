import pygame
import random
import copy
import pygame_button
from grid import Grid
from ships import Ships


retry = False


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BUTTON_COLOR = WHITE

block_size = 50
left_margin = 80
upper_margin = 70

screen_size = (left_margin + 30 * block_size, upper_margin + 15 * block_size)
button_size_x = (screen_size[0] - left_margin - block_size * 5 - 60) // 4
button_size_y = button_size_x // 3
button_top_border = int(upper_margin + block_size * 11.5)

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

game_over = False

pygame.init()

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Morskoy Boy v 1.1")

font_size = int(block_size / 1.5)

font = pygame.font.SysFont('notosans', font_size)
computer_available_to_fire_set = {(x, y) for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
hit_blocks = set()
dotted_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
destroyed_computer_ships = []


class ShootHandler:
    """
    Class for handling shooting logic. Used both for human and computer shots proceeding
    Arguments
    ----------
    Methods
    ----------
        computer_shoots(self, set_to_shoot_from): Randomly chooses a block from argument set for the computer shot
        check_hit_or_miss(sels, fired_block, opponent_ships_list, computer_turn, opponnents_ships_list_original_copy,
            opponnents_ship_list): Checks if the shot block belongs to ship or not. Updates blocks to be dotted
            (diagonal around hit blocks or missed one) and blocks to be marked as hit. Removes destroyed ships
            from the list of alive
        __update_destroyed ships(self, ind, computer_turn, opponnents_ships_list_original_copy):
            Updates blocks surrounding the ship, making them dotted. Adds all blocks in a ship to the list of hit ones
        __update_around_last_computer_hit(self, fired_block, computer_turn): Updates the set computer chooses the block
            to shoot at from in case the computer hit but didn't destroyed the ship.
        __computer_first_hit(self, fired_block): Updates the set computer chooses the block to shoot at from after it's
            first hit.
        __computer_hits_multiple(self): Updates the set computer chooses the block to shoot at from after it had hit
            two or more blocks of one ship.
        __update_dotted_and_hit_sets(self, fired_block, computer_turn, diagonal_only=True): Updates dotted and hit sets
            after either computer and human shots
        __add_missed_block_to_dotted_set(self, fired_block): Updates the dotted set with a block shot in case
            the ship was not hit
    """
    def __init__(self):
        self.computer_fired_block = None
        self.x_hit, self.y_hit = None, None
        self.x1, self.x2, self.y1, self.y2 = None, None, None, None

    def computer_shoots(self, set_to_shoot_from):
        """
        Randomly chooses a block from available to shoot from set
        """
        global game_over
        if human.opponent_hits_counter < 20:
            pygame.time.delay(500)
            self.computer_fired_block = random.choice(tuple(set_to_shoot_from))
            computer_available_to_fire_set.discard(self.computer_fired_block)
            return self.computer_fired_block
        else:
            game_over = True

    def check_hit_or_miss(self, fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                          opponents_ships_set):
        """
        Checks whether the block that was shot at either by computer or by human is a hit or a miss.
        Updates sets with dots (in missed blocks or in diagonal blocks around hit block) and 'X's
        (in hit blocks).
        Removes destroyed ships from the list of ships.
        """
        for elem in opponents_ships_list:
            diagonal_only = True
            if fired_block in elem:
                # This is to put dots before and after a destroyed ship
                # and to draw computer's destroyed ships (which are hidden until destroyed)
                ind = opponents_ships_list.index(elem)
                if len(elem) == 1:
                    diagonal_only = False
                self.__update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only)
                elem.remove(fired_block)
                # This is to check who loses - if ships_set is empty
                opponents_ships_set.discard(fired_block)
                if computer_turn:
                    last_hits_list.append(fired_block)
                    self.__update_around_last_computer_hit(fired_block, True)
                    human.opponent_hits_counter += 1
                else:
                    computer.opponent_hits_counter += 1
                # If the ship is destroyed
                if not elem:
                    self.__update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy)
                    if computer_turn:
                        last_hits_list.clear()
                        around_last_computer_hit_set.clear()
                    else:
                        # Add computer's destroyed ship to the list to draw it (computer ships are hidden)
                        destroyed_computer_ships.append(computer.ships[ind])
                return True
        self.__add_missed_block_to_dotted_set(fired_block)
        if computer_turn:
            self.__update_around_last_computer_hit(fired_block, False)
        return False

    def __update_destroyed_ships(self, ind, computer_turn, opponents_ships_list_original_copy):
        """
        Adds blocks before and after a ship to dotted_set to draw dots on them.
        Adds all blocks in a ship to hit_blocks set to draw 'X's within a destroyed ship.
        """
        ship = sorted(opponents_ships_list_original_copy[ind])
        for i in range(-1, 1):
            self.__update_dotted_and_hit_sets(ship[i], computer_turn, False)

    def __update_around_last_computer_hit(self, fired_block, computer_hits):
        """
        Updates around_last_computer_hit_set (which is used to choose for computer to fire from) if it
        hit the ship but not destroyed it). Adds to this set vertical or horizontal blocks around the
        block that was last hit. Then removes those block from that set which were shot at but missed.
        around_last_computer_hit_set makes computer choose the right blocks to quickly destroy the ship
        instead of just randomly shooting at completely random blocks.
        """
        global around_last_computer_hit_set, computer_available_to_fire_set
        if computer_hits and fired_block in around_last_computer_hit_set:
            around_last_computer_hit_set = self.__computer_hits_multiple()
        elif computer_hits and fired_block not in around_last_computer_hit_set:
            self.__computer_first_hit(fired_block)
        elif not computer_hits:
            around_last_computer_hit_set.discard(fired_block)

        around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
        around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
        computer_available_to_fire_set -= around_last_computer_hit_set
        computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot

    def __computer_first_hit(self, fired_block):
        """
        Adds blocks above, below, to the right and to the left from the block hit
        by computer to a temporary set for computer to choose its next shot from.
        Args:
            fired_block (tuple): coordinates of a block hit by computer
        """
        self.x_hit, self.y_hit = fired_block
        if self.x_hit > 16:
            around_last_computer_hit_set.add((self.x_hit - 1, self.y_hit))
        if self.x_hit < 25:
            around_last_computer_hit_set.add((self.x_hit + 1, self.y_hit))
        if self.y_hit > 1:
            around_last_computer_hit_set.add((self.x_hit, self.y_hit - 1))
        if self.y_hit < 10:
            around_last_computer_hit_set.add((self.x_hit, self.y_hit + 1))

    def __computer_hits_multiple(self):
        """
        Adds blocks before and after two or more blocks of a ship to a temporary list
        for computer to finish the ship faster.
        Returns:
            set: temporary set of blocks where potentially a human ship should be
            for computer to shoot from
        """
        last_hits_list.sort()
        new_around_last_hit_set = set()
        for i in range(len(last_hits_list) - 1):
            self.x1 = last_hits_list[i][0]
            self.x2 = last_hits_list[i + 1][0]
            self.y1 = last_hits_list[i][1]
            self.y2 = last_hits_list[i + 1][1]
            if self.x1 == self.x2:
                if self.y1 > 1:
                    new_around_last_hit_set.add((self.x1, self.y1 - 1))
                if self.y2 < 10:
                    new_around_last_hit_set.add((self.x1, self.y2 + 1))
            elif self.y1 == self.y2:
                if self.x1 > 16:
                    new_around_last_hit_set.add((self.x1 - 1, self.y1))
                if self.x2 < 25:
                    new_around_last_hit_set.add((self.x2 + 1, self.y1))
        return new_around_last_hit_set

    def __update_dotted_and_hit_sets(self, fired_block, computer_turn, diagonal_only=True):
        """
        Puts dots in center of diagonal or all around a block that was hit (either by human or
        by computer). Adds all diagonal blocks or all-around chosen block to a separate set
        block: hit block (tuple)
        """
        global dotted_set
        x, y = fired_block
        a = 15 * computer_turn
        b = 11 + 15 * computer_turn
        # Adds a block hit by computer to the set of his hits to later remove
        # them from the set of blocks available for it to shoot from
        hit_blocks_for_computer_not_to_shoot.add(fired_block)
        # Adds hit blocks on either grid1 (x:1-10) or grid2 (x:16-25)
        hit_blocks.add(fired_block)
        # Adds blocks in diagonal or all-around a block to repsective sets
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                    self.__add_missed_block_to_dotted_set((x + i, y + j))
        dotted_set -= hit_blocks

    def __add_missed_block_to_dotted_set(self, fired_block):
        """
        Adds a fired_block to the set of missed shots (if fired_block is a miss then) to then draw dots on them.
        Also needed for computer to remove these dotted blocks from the set of available blocks for it to shoot from.
        """
        dotted_set.add(fired_block)
        dotted_set_for_computer_not_to_shoot.add(fired_block)


class DrawShips:
    """
    Dedicated to handle displaying of ships on either computer' and humans' grids
    Attributes
    ----------
        window (pygame.screen): surface to display everything on
        margin_left (int): left margin of window
        margin_top (int): upper margin of window
    Methods

    ----------
    """
    def __init__(self, window, margin_left, margin_top):
        self.screen = window
        self.left_margin = margin_left
        self.upper_margin = margin_top
        self.ship = None
        self.x_start = None
        self.y_start = None
        self.ship_height = None
        self.ship_width = None
        self.x = None
        self.y = None

    def draw_ships(self, ships_coordinates_list):
        """
        Draws rectangles around the blocks that are occupied by a ship
        Args:
            ships_coordinates_list (list of tuples): a list of ships's coordinates
        """
        for elem in ships_coordinates_list:
            self.ship = sorted(elem)
            self.x_start = self.ship[0][0]
            self.y_start = self.ship[0][1]
            # Horizontal and 1block ships
            self.ship_width = block_size * len(self.ship)
            self.ship_height = block_size
            # Vertical ships
            if len(self.ship) > 1 and self.ship[0][0] == self.ship[1][0]:
                self.ship_width, self.ship_height = self.ship_height, self.ship_width
            self.x = block_size * (self.x_start - 1) + self.left_margin
            self.y = block_size * (self.y_start - 1) + self.upper_margin
            pygame.draw.rect(
                self.screen, BLACK, ((self.x, self.y), (self.ship_width, self.ship_height)), width=block_size // 10)

    def draw_from_dotted_set(self, dotted_set_to_draw_from):
        """
        Draws dots in the center of all blocks in the dotted_set
        """
        global game_over
        if human.opponent_hits_counter < 20:
            for elem in dotted_set_to_draw_from:
                pygame.draw.circle(self.screen, BLACK, (block_size * (
                        elem[0] - 0.5) + self.left_margin, block_size * (elem[1] - 0.5) + self.upper_margin),
                                   block_size // 6)
        else:
            game_over = True

    def draw_hit_blocks(self, hit_blocks_to_draw_from):
        """
        Draws crosses in the blocks that were successfully hit either by computer or by human
        """
        for block in hit_blocks_to_draw_from:
            self.x = block_size * (block[0] - 1) + self.left_margin
            self.y = block_size * (block[1] - 1) + self.upper_margin
            pygame.draw.line(self.screen, BLACK, (self.x, self.y),
                             (self.x + block_size, self.y + block_size), block_size // 6)
            pygame.draw.line(screen, BLACK, (self.x, self.y + block_size),
                             (self.x + block_size, self.y), block_size // 6)


draw = DrawShips(screen, left_margin, upper_margin)
computer = Ships(0, True)
human = Ships(15)
computer_ships_working = copy.deepcopy(computer.ships)
human_ships_working = copy.deepcopy(human.ships)


def change_retry():
    global retry
    retry = not retry


def main():
    global game_over
    game_over = False
    computer_turn = False
    screen.fill(WHITE)
    Grid("COMPUTER", 0, screen, (LETTERS, BLACK, left_margin, upper_margin, block_size, font, font_size))
    Grid("HUMAN", 15, screen, (LETTERS, BLACK, left_margin, upper_margin, block_size, font, font_size))
    shoot = ShootHandler()
    # Buttons for creating ships. Now useless
    one_cell_button = pygame_button.Button((left_margin, button_top_border, button_size_x, button_size_y),
                                           BUTTON_COLOR, None,
                                           **{'text': "1-cell: 4", 'font': font, 'font_color': BLACK,
                                              'hover_color': GRAY})
    two_cell_button = pygame_button.Button((left_margin + button_size_x + 20, button_top_border, button_size_x,
                                            button_size_y),
                                           BUTTON_COLOR, None,
                                           **{'text': "2-cell: 3", 'font': font, 'font_color': BLACK,
                                              'hover_color': GRAY})
    three_cell_button = pygame_button.Button((left_margin + (button_size_x + 20) * 2, button_top_border, button_size_x,
                                              button_size_y),
                                             BUTTON_COLOR, None,
                                             **{'text': "3-cell: 2", 'font': font, 'font_color': BLACK,
                                                'hover_color': GRAY})
    four_cell_button = pygame_button.Button((left_margin + (button_size_x + 20) * 3, button_top_border, button_size_x,
                                             button_size_y),
                                            BUTTON_COLOR, None,
                                            **{'text': "4-cell: 1", 'font': font, 'font_color': BLACK,
                                               'hover_color': GRAY})

    ship_buttons = (
        one_cell_button,
        two_cell_button,
        three_cell_button,
        four_cell_button)

    draw.draw_ships(human.ships)
    draw.draw_ships(computer.ships)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or computer.opponent_hits_counter == 20 or human.opponent_hits_counter == 20:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin < x < left_margin + 10 * block_size) and (
                        upper_margin < y < upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                    computer_turn = not shoot.check_hit_or_miss(fired_block, computer_ships_working, False,
                                                                computer.ships, computer.ships_set)

        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = shoot.computer_shoots(set_to_shoot_from)
            computer_turn = shoot.check_hit_or_miss(fired_block, human_ships_working, True,
                                                    human.ships, human.ships_set)

        draw.draw_from_dotted_set(dotted_set)
        draw.draw_hit_blocks(hit_blocks)
        draw.draw_ships(destroyed_computer_ships)
        for button in ship_buttons:
            button.update(screen)
        pygame.display.update()


def rerun():
    global retry
    global game_over
    restart_button = pygame_button.Button((screen_size[0] // 4, screen_size[1] * 2 // 3, screen_size[0] // 2, 60),
                                          WHITE, change_retry,
                                          **{'text': "CLICK TO RETRY",
                                             'font': pygame.font.SysFont('notosans', int(block_size * 1.5)),
                                             'hover_color': GRAY,
                                             'font_color': BLACK})
    win_sign = "{} won"
    game_over = not game_over

    if computer.opponent_hits_counter == 20:
        win_sign_to_draw = font.render(win_sign.format("You"), True, BLACK)
        win_sign_width = win_sign_to_draw.get_width()
        win_sign_height = win_sign_to_draw.get_height()
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                restart_button.check_event(event)
            screen.fill(WHITE)
            screen.blit(win_sign_to_draw, ((screen_size[0] - win_sign_width) // 2,
                                           (screen_size[1] - win_sign_height) // 2))
            restart_button.update(screen)
            pygame.display.update()
    elif human.opponent_hits_counter == 20:
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                else:
                    win_sign_to_draw = font.render(win_sign.format("Computer"), True, BLACK)
                    win_sign_width = win_sign_to_draw.get_width()
                    win_sign_height = win_sign_to_draw.get_height()
                    screen.blit(win_sign_to_draw, ((screen_size[0] - win_sign_width) // 2,
                                                   (screen_size[1] - win_sign_height) // 2))
                    restart_button.update(screen)
                    pygame.display.update()
    pass


while True:
    main()
    rerun()
    if retry is True:
        pass
    else:
        break

pygame.quit()
