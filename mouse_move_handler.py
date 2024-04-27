from player import Player


class MouseMoveHandler:
    def handle_movement(self, player, coord):
        player_moved = False

        player_data = player.player_data
        dx = coord[0] - player_data.coord[0]
        dy = coord[1] - player_data.coord[1]
        distance = max(abs(dx), abs(dy))  # Maximum of horizontal and vertical distance
        if distance != 0:
            speed = 2  # Adjust speed as needed (slower)
            player_data.coord = (player_data.coord[0] + int(dx / distance * speed),
                                 player_data.coord[1] + int(dy / distance * speed))
            player_moved = True
        return player_moved