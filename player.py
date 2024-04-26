import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, player_data):
        self.player_data = player_data

    def draw(self, screen):
        # Draw the outer circle
        player_data = self.player_data
        pygame.draw.circle(screen,  player_data.color, (player_data.coord[0], player_data.coord[1]), player_data.radius + 2)
        pygame.draw.circle(screen, pygame.Color("black"), (player_data.coord[0], player_data.coord[1]), player_data.radius)


    def update(self: object, target_pos: object) -> object:
        player_data = self.player_data
        dx = target_pos[0] - player_data.coord[0]
        dy = target_pos[1] - player_data.coord[1]
        distance = max(abs(dx), abs(dy))  # Maximum of horizontal and vertical distance
        if distance != 0:
            speed = 2  # Adjust speed as needed (slower)
            player_data.coord = (player_data.coord[0] + int(dx / distance * speed),
                                 player_data.coord[1] + int(dy / distance * speed))