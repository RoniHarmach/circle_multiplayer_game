class PlayerUtils:

    @staticmethod
    def get_scores_sum(swallowed_players):
        return sum(player.score for player in swallowed_players)

    @staticmethod
    def get_radii_sum(swallowed_players):
        return sum(player.radius for player in swallowed_players)

    @staticmethod
    def get_players_numbers(players):
        return [player.player_number for player in players]