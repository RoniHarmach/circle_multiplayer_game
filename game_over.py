import pygame
from pygame.sprite import Sprite
from PIL import Image


class GameOver(Sprite):


    def __init__(self):
        super().__init__()

        self.i = 0

    def draw(self, screen):
        pygame.display.set_caption("Transparent Image Label")
        image = pygame.image.load("sprite/game_over7.png")  # Replace "image_with_transparency.png" with your image file
        # image.set_colorkey((255, 255, 255))  # Set white as the transparent color
        # surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        # surface.fill((255, 255, 255, 128))  # Fill with white background color
        # surface.blit(image, (190, 30))  # Adjust the position as needed
        # screen.blit(surface, (0, 0))

        image_rect = image.get_rect()
        screen_width, screen_height = screen.get_size()
        image_rect.center = (screen_width // 2, screen_height // 2)
        image.set_alpha(128)
        screen.blit(image, image_rect)

    def draw2(self, screen):
        image = pygame.image.load("sprite/game_over8.png")  # Replace "game_over7.png" with your image file
        image.set_colorkey((255, 255, 255))  # Set white as the transparent color
        surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        surface.fill((255, 255, 255, 128))  # Fill with white background color
        screen_width, screen_height = screen.get_size()
        image_width, image_height = image.get_size()
        # Calculate the position to blit the image, keeping it within the screen boundaries
        blit_x = max(0, (screen_width - image_width) // 2)  # Ensure blit_x is not less than 0
        blit_y = max(0, (screen_height - image_height) // 2)  # Ensure blit_y is not less than 0
        surface.blit(image, (blit_x, blit_y))  # Adjust the position as needed
        screen.blit(surface, (0, 0))
