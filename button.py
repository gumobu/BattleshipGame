import pygame_button


class Button:
    def __init__(self, x_bottom, y_bottom, size_x, size_y, func_number, text, font,
                 inactive_font_color, inactive_button_color,
                 hover_button_color):
        self.x = x_bottom
        self.y = y_bottom
        self.size_x = size_x
        self.size_y = size_y
        self.func_number = func_number
        self.button_text = text
        self.font = font
        self.inactive_font_color = inactive_font_color
        self.inactive_button_color = inactive_button_color
        self.hover_button_color = hover_button_color
        self.func = None

    def create(self):
        self.func = self.__func_determine()
        pygame_button.Button((self.x, self.y, self.size_x, self.size_y),
                             self.inactive_button_color, self.func(),
                             **{'text': self.button_text, 'font': self.font,
                                'font_color': self.inactive_font_color,
                                'hover_color': self.hover_button_color,
                                'call_on_release': True})

    def __func_determine(self):
        if self.func_number == 1:
            return self.__build_ship
        elif self.func_number == 2:
            return self.__restart_function

    def __restart_function(self):
        main()

    def __build_ship(self):
        pass
