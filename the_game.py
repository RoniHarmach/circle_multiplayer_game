import pygame
import math
from player import Player
from player_utils import PlayerUtils
from player_data import PlayerData
pygame.init()

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)

class Static_Dot(pygame.sprite.Sprite):
    def __init__(self, x, y, color, radius):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


"""def check_collision(players):
    for i, player1 in enumerate(players):
        for j, player2 in enumerate(players):
            if i != j:  # Avoid self-collision
                # Calculate distance between center points
                distance = math.sqrt((player1.x - player2.x) ** 2 + (player1.y - player2.y) ** 2)

                # Check if circles overlap
                if distance < player1.radius + player2.radius:
                    # Check if player1 is smaller than player2
                    if player1.radius < player2.radius:
                        return i, j  # Player 1 is on top of Player 2
                    else:
                        return j, i  # Player 2 is on top of Player 1
    return None
"""


dots = [
    Static_Dot(100, 60, (255, 182, 193), 6),
    Static_Dot(200, 400, (255, 182, 193), 6),
    Static_Dot(100, 160, (255, 182, 193), 6),
    Static_Dot(160, 340, (255, 182, 193), 6),
    Static_Dot(100, 100, (255, 182, 193), 6),
    Static_Dot(400, 120, (255, 182, 193), 6),
    Static_Dot(100, 140, (255, 182, 193), 6)

]

player = Player(PlayerData(543, 413, BLUE, 22))  # Create player with position (100, 100) and radius 20
player2 = Player(PlayerData(213, 122, RED, 1))  # Create another player with position (200, 200) and radius 20

players = [
    player,  # Create player with position (100, 100) and radius 20
    player2,  # Create another player with position (200, 200) and radius 20
]

running = True
screen = pygame.display.set_mode((WIDTH, HEIGHT))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)
    # Update
    mouse_pos = pygame.mouse.get_pos()

    player.update(mouse_pos)

    # Draw

    clock = pygame.time.Clock()

    screen.fill((255, 255, 255))  # Fill the screen with black

    PlayerUtils.handle_Static_Dot_collision(players, dots)

    for dot in dots:
        dot.draw(screen)

    if len(players) > 1:
        PlayerUtils.handle_collision(players)
        if player in players:
            player.draw(screen)
        if player2 in players:
            player2.draw(screen)
    else:
        player.draw(screen)
    pygame.display.update()

    pygame.time.Clock().tick(40)  # Limit to 60 frames per second

pygame.quit()
