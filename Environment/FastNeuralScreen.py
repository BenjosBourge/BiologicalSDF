
import pygame
import numpy as np
import math

class FastNeuralScreen:
    def __init__(self, x, y, solver, nb_tiles=51):
        self.x = x
        self.y = y
        self.range = 10.
        self.solver = solver
        self.sdfMode = False
        self.step_value = 0.2
        self.show_loss = True
        self.show_range = False
        self.nb_tiles = nb_tiles
        self.font = pygame.font.Font(None, 36)
        self.font_range = pygame.font.Font(None, 24)
        self.grid = np.zeros((nb_tiles, nb_tiles), dtype=float)

    def update(self, delta_time, scroll):
        pass

    def setSDFMode(self, mode):
        self.sdfMode = mode

    def getColor(self, value):
        color2 = (230, 126, 34)
        color1 = (52, 152, 219)
        value = max(0, min(value, 1))

        color1 = [color1[0], color1[1], color1[2]]
        color2 = [color2[0], color2[1], color2[2]]

        if value <= 0.5:
            factor = value / 0.5
            r = color1[0] * (1 - factor) + 255 * factor
            g = color1[1] * (1 - factor) + 255 * factor
            b = color1[2] * (1 - factor) + 255 * factor
        else:
            factor = (value - 0.5) / 0.5
            r = 255 * (1 - factor) + color2[0] * factor
            g = 255 * (1 - factor) + color2[1] * factor
            b = 255 * (1 - factor) + color2[2] * factor

        return (r, g, b)

    def getColorMatrix(self, value, predicted_value):
        color = (0, 0, 0)
        if value == 1:
            if predicted_value == 1:
                color = (0, 255, 0)  # TP = GREEN
            else:
                color = (255, 0, 255)  # FN = PURPLE
        else:
            if predicted_value == 1:
                color = (255, 255, 0)  # FP = YELLOW
            else:
                color = (255, 0, 0)  # TN = RED
        return color

    def update_grid(self):
        for row in range(self.nb_tiles):
            for col in range(self.nb_tiles):
                value = self.solver.solve((col / ((self.nb_tiles - 1)/2) - 1.) * self.range, (row / ((self.nb_tiles - 1)/2) - 1.) * -1 * self.range)
                if self.sdfMode:
                    if value < 0:
                        value = math.floor(-value / 0.01) * 2. * -1
                    else:
                        value = math.floor(value / self.step_value) * 0.2
                    value = (value + 1) / 2.0
                self.grid[row][col] = value

    def draw(self, screen):
        for row in range(self.nb_tiles):
            for col in range(self.nb_tiles):
                value = self.grid[row][col]
                color = self.getColor(value)
                rect = pygame.Rect(col * (306 / self.nb_tiles) + self.x, row * (306 / self.nb_tiles) + self.y, 306 / (self.nb_tiles - 1), 306 / (self.nb_tiles - 1))
                pygame.draw.rect(screen, color, rect)

        if self.show_loss:
            text_surface = self.font.render(str(self.solver.getLoss()), True, (255, 255, 255))
            screen.blit(text_surface, (self.x, self.y - 25))

        if self.show_range:
            text_surface = self.font_range.render(f"{self.range:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (self.x - 40, self.y - 5))
            text_surface = self.font_range.render(f"{-self.range:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (self.x - 40, self.y + 306 - 15))
            text_surface = self.font_range.render(f"{self.range:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (self.x + 306 - 20, self.y + 306 + 10))
            text_surface = self.font_range.render(f"{-self.range:.2f}", True, (255, 255, 255))
            screen.blit(text_surface, (self.x - 5, self.y + 306 + 10))

    def draw_datas(self, screen, datas, values):
        for i in range(datas.shape[0]):
            x = datas[i][0]
            y = datas[i][1]

            value = values[i][0]
            predicted_value = self.solver.solve(x, y)
            if predicted_value < 0.5:
                predicted_value = 0
            else:
                predicted_value = 1
            color = self.getColorMatrix(value, predicted_value)

            pygame.draw.circle(screen, color, (150 + x * 15 + self.x, 150 + y * 15 + self.y), 3)

