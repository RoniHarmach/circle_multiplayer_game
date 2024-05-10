import pygame

from game_constants import OUTER_CIRCLE_SIZE


class Player(pygame.sprite.Sprite):

    def __init__(self, player_data):
        super().__init__()
        self.player_data = player_data

    def draw(self, screen):
        # Draw the outer circle
        player_data = self.player_data

        pygame.draw.circle(screen,  player_data.color, (player_data.coord[0], player_data.coord[1]), player_data.radius + OUTER_CIRCLE_SIZE)
        pygame.draw.circle(screen, pygame.Color("black"), (player_data.coord[0], player_data.coord[1]), player_data.radius)

