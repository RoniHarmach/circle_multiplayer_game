import pygame
from player_data import PlayerData
BLACK = (0, 0, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self, player_data):
        self.player_data = player_data
        # self.x = player_data.x
        # self.y = player_data.y
        # self.color = player_data.color
        # self.radius = player_data.radius
        # self.outer_radius = player_data.outer_radius  # Adjusted outer radius
        # self.num_circles = player_data.num_circles

    def draw(self, screen):
        # Draw the outer circle
        player_data = self.player_data
        pygame.draw.circle(screen,  player_data.color, (player_data.x, player_data.y), player_data.radius + 2)
        pygame.draw.circle(screen, BLACK, (player_data.x, player_data.y), player_data.radius)
        inner_radius = player_data.outer_radius // player_data.num_circles
        for i in range(player_data.num_circles):
            radius = inner_radius * (i + 1)
            pygame.draw.circle(screen, (150, 150, 150), (player_data.x, player_data.y), radius)

    """    def draw(self, screen):
            pygame.draw.circle(screen,  self.color, (self.x, self.y), self.radius + 2)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius)
    """
    def update(self: object, target_pos: object) -> object:
        player_data = self.player_data
        dx = target_pos[0] - player_data.x
        dy = target_pos[1] - player_data.y
        distance = max(abs(dx), abs(dy))  # Maximum of horizontal and vertical distance
        if distance != 0:
            speed = 2  # Adjust speed as needed (slower)
            player_data.x += dx / distance * speed
            player_data.y += dy / distance * speed
