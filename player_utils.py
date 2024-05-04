import math


class PlayerUtils:


    @staticmethod
    def check_collision(player_data, coord, radius):
        if player_data.radius < radius:
            return False
        distance = math.sqrt((player_data.coord[0] - coord[0]) ** 2 + (player_data.coord[1] - coord[1]) ** 2)
        if distance <= player_data.radius - radius:
            return True
        else:
            return False

    @staticmethod
    def get_scores_sum(swallowed_players):
        return sum(player.score for player in swallowed_players)

    @staticmethod
    def get_playerS_numbers(players):
        return [player.player_number for player in players]