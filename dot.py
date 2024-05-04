import pygame


class Dot(pygame.sprite.Sprite):

    def __init__(self, dot_data):
        super().__init__()
        self.dot_data = dot_data

    def draw(self, screen):
        dot_data = self.dot_data
        pygame.draw.circle(screen,  dot_data.color, (dot_data.coord[0], dot_data.coord[1]), dot_data.radius)

