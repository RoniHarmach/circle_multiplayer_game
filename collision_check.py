import pygame
import sys

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WIDTH, HEIGHT = 800, 600

# Create the window surface
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load the images for the sprites
sprite1_image = pygame.image.load("sprite/circle1.png").convert_alpha()
sprite2_image = pygame.image.load("sprite/circle2.png").convert_alpha()

# Create masks for the sprites
sprite1_mask = pygame.mask.from_surface(sprite1_image)
sprite2_mask = pygame.mask.from_surface(sprite2_image)

# Set the initial positions of the sprites
sprite1_rect = sprite1_image.get_rect(center=(WIDTH // 3 + 140, HEIGHT // 2))
sprite2_rect = sprite2_image.get_rect(center=(2 * WIDTH // 3, HEIGHT // 2))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for collision between the masks of the sprites
    if sprite1_mask.overlap(sprite2_mask, (sprite2_rect.x - sprite1_rect.x, sprite2_rect.y - sprite1_rect.y)):
        print("Collision detected!")

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the sprites
    screen.blit(sprite1_image, sprite1_rect)
    screen.blit(sprite2_image, sprite2_rect)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
