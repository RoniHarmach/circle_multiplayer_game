import math


class PlayerUtils:
    @staticmethod
    def check_collision(players):
        for i, player1 in enumerate(players):
            for j, player2 in enumerate(players):
                if i != j:  # Avoid self-collision
                    # Calculate distance between center points
                    distance = math.sqrt((player1.player_data.x - player2.player_data.x) ** 2 + (player1.player_data.y - player2.player_data.y) ** 2)

                    # Check if circles overlap and player1 is smaller than player2
                    if distance < player1.player_data.radius + player2.player_data.radius and player1.player_data.radius < player2.player_data.radius:
                        return i, j  # Player 1 is touching a bigger Player 2
        return None

    @staticmethod
    def handle_collision(players):
        collision = PlayerUtils.check_collision(players)
        if collision is not None:
            index_eaten, index_eater = collision
            player_eaten = players[index_eaten]
            player_eater = players[index_eater]
            if player_eaten.player_data.radius < player_eater.player_data.radius:
                player_eater.player_data.radius *= 1.1  # Increase radius of eater player by 10%
                players.remove(player_eaten)  # Remove eaten player from the list
                return player_eaten, player_eater
        return None, None

    @staticmethod
    def check_Static_Dot_collision(players, static_dots):
        for i, player in enumerate(players):
            playerData = player.player_data
            for circle in static_dots:
                # Calculate distance between player and circle center points
                distance = math.sqrt((playerData.x - circle.x) ** 2 + (playerData.y - circle.y) ** 2)

                # Check if player overlaps with circle
                if distance < playerData.radius + circle.radius:
                    return i, circle  # Player collided with circle
        return None, None

    @staticmethod
    def handle_Static_Dot_collision(players, static_circles):
        collision_index, collided_circle = PlayerUtils.check_Static_Dot_collision(players, static_circles)

        if collision_index is not None:
            player = players[collision_index]
            player.player_data.radius *= 1.08 # Increase player radius by 5%
            del static_circles[static_circles.index(collided_circle)]  # Remove collided circle
            return player, collided_circle
        return None, None
