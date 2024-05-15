from game_constants import *


class MouseMoveHandler:

    def allow_player_movement(self, player, coord):
        player_data = player.player_data
        if self.moved_left(player.player_data, coord) and self.exit_left_side(player_data, coord):
            return False
        if self.moved_right(player.player_data, coord) and self.exit_right_side(player_data, coord):
            return False
        if self.moved_up(player_data, coord) and self.exit_top_side(player_data, coord):
            return False
        if self.moved_down(player.player_data, coord) and self.exit_bottom_side(player_data, coord):
            return False
        return True

    def moved_left(self, player_data, coord):
        return player_data.coord[0] > coord[0]

    def moved_right(self, player_data, coord):
        return player_data.coord[0] < coord[0]

    def moved_up(self, player_data, coord):
        return player_data.coord[1] > coord[1]

    def moved_down(self, player_data, coord):
        return player_data.coord[1] < coord[1]

    def exit_left_side(self, player_data, coord):
        return coord[0] - player_data.radius - OUTER_CIRCLE_SIZE < 0

    def exit_right_side(self, player_data, coord):
        return coord[0] + player_data.radius + OUTER_CIRCLE_SIZE > SCREEN_WIDTH

    def exit_top_side(self, player_data, coord):
        return coord[1] - player_data.radius - SCORE_BOARD_HEIGHT - OUTER_CIRCLE_SIZE < 0

    def exit_bottom_side(self, player_data, coord):
        return coord[1] + player_data.radius + OUTER_CIRCLE_SIZE > SCREEN_HEIGHT

    def handle_movement(self, player, coord):
        player_moved = False

        player_data = player.player_data
        dx = coord[0] - player_data.coord[0]
        dy = coord[1] - player_data.coord[1]
        distance = max(abs(dx), abs(dy))  # Maximum of horizontal and vertical distance
        speed = 2
        if distance == 0:
            return player_moved
        dx_change = player_data.coord[0] + int(dx / distance * speed)
        dy_change = player_data.coord[1] + int(dy / distance * speed)
        if distance > 5 and self.allow_player_movement(player, [dx_change, dy_change]):
            player_data.coord = (dx_change, dy_change)
            player_moved = True

        return player_moved
