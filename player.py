import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, player_data):
        self.player_data = player_data

    def draw(self, screen):
        # Draw the outer circle
        player_data = self.player_data
        pygame.draw.circle(screen,  player_data.color, (player_data.coord[0], player_data.coord[1]), player_data.radius + 2)
        pygame.draw.circle(screen, pygame.Color("black"), (player_data.coord[0], player_data.coord[1]), player_data.radius)

