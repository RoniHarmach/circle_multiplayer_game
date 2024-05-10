from tkinter import font
import pygame
from pygame.sprite import Sprite


class ScoreBoard(Sprite):

    def __init__(self):
        super().__init__()

    def create_label(self, label, player_data):
        font = pygame.font.Font(None, 36)
        return font.render(label, True, pygame.Color("black"), pygame.Color(player_data.color))

    def update_state(self, player, other_players):
        sorted_other_players = sorted(other_players, key=lambda other_playr: other_playr.player_number)
        #labels = [f"your player score:{player.score}"]
        print("update score board")
        self.labels = []
        current_player_label = self.create_label(f"Your Player {player.player_number} score:{player.score}", player)
        self.labels.append((current_player_label, (1, 5)))

        for index, other_player in enumerate(sorted_other_players):
            label = self.create_label(f"Player {other_player.player_number} score:{other_player.score}", other_player)
            self.labels.append((label, ((index + 1)* 400, 5)))


    def draw(self, screen):
        rect = pygame.Rect(0, 0, 1100, 40)
        pygame.draw.rect(screen, pygame.Color("gray"), rect)
        for label_surface, pos in self.labels:
            screen.blit(label_surface, pos)





