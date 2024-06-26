from dataclasses import dataclass
from typing import Dict
from collision_utils import CollisionUtils
from dot_data import DotData
from dot_utils import DotUtils
from game_constants import *
from player_state import PlayerState


@dataclass
class GameManager:
    next_dot_id = 1
    players_states: Dict[int, PlayerState] = None
    dots: Dict[int, DotData] = None

    def __init__(self):
        self.players_states: Dict[int, PlayerState] = {}

    def add_player_state(self, player_number, player_state):
        self.players_states[player_number] = player_state

    def add_player_data(self, player_number, player_data):
        state = self.players_states[player_number]
        state.player_data = player_data


    def get_players_data(self):
        return {key: player_state.player_data for key, player_state in self.players_states.items()}

    def get_other_players_data(self, player_number):
        return {key: player_state.player_data for key, player_state in self.players_states.items() if
                         key != player_number}

    def get_player_data(self, player_number):
        return self.players_states[player_number].player_data

    def get_dot_data(self, dot_id):
        return self.dots[dot_id]

    def get_player_is_alive(self, player_number):
        return self.players_states[player_number].player_data.is_alive

    def set_player_is_alive(self, player_number, is_alive):
        self.players_states[player_number].player_data.is_alive = is_alive

    def set_client_disconnected(self, player_number):
        self.players_states[player_number].connected = False
        self.players_states[player_number].client_socket = None

    def update_position(self, player_number, coord):
        self.players_states[player_number].player_data.coord = coord

    def get_player_position(self, player_number):
        return self.players_states[player_number].player_data.coord

    def get_player_score(self, player_number):
        return self.players_states[player_number].player_data.score

    def set_player_ready(self, player_number):
        self.players_states[player_number].player_ready = True

    def is_ready(self):
        return all(player_state.player_ready for player_state in self.players_states.values()) \
            and len(self.players_states) == NUM_OF_PLAYERS

    def get_live_players(self):
        return [player_state.player_data for player_state in self.players_states.values()
         if player_state.player_data.is_alive is True]

    def get_all_connected_player_numbers(self):
        return [key for key, player_state in self.players_states.items() if player_state.connected]

    def is_connected(self, player_number):
        return self.players_states[player_number].connected


    def get_client_socket(self, player_number):
        return self.players_states[player_number].client_socket

    def is_all_players_joined(self):
        return len(self.players_states) == NUM_OF_PLAYERS

    def initialize_dots(self):
        self.dots = {}
        for i in range(1, MAX_NUM_OF_DOTS):
            GameManager.create_random_dot(self)
        return self.dots

    def get_other_live_players(self, player_number):
        return [player_state.player_data for player_state in self.players_states.values()
                if player_state.player_data.player_number != player_number
                and player_state.player_data.is_alive is True]

    def dot_touches_player(self, new_dot):
        for player in self.players_states:
            if (CollisionUtils.check_new_dot_collision(self.players_states[player].player_data.coord, self.players_states[player].player_data.radius, new_dot.coord, new_dot.radius) and\
                    CollisionUtils.check_new_dot_collision(new_dot.coord, new_dot.radius, self.players_states[player].player_data.coord, self.players_states[player].player_data.radius)):
                return True
        return False

    def dot_touches_other_dot(self, dot):
        return any(CollisionUtils.check_new_dot_collision(dot.coord, dot.radius, other_dot.coord, other_dot.radius) or
                   CollisionUtils.check_new_dot_collision(other_dot.coord, other_dot.radius, dot.coord, dot.radius)
                   for other_dot in self.dots.values())

    def create_random_dot(self):
        dot = DotUtils.create_random_dot(self.next_dot_id)
        while self.dot_touches_player(dot) or self.dot_touches_other_dot(dot):
            dot = DotUtils.create_random_dot(self.next_dot_id)
        self.dots[self.next_dot_id] = dot
        self.next_dot_id += 1
        return dot

    def create_missing_dot(self):
        dot = None
        if len(self.dots) < MAX_NUM_OF_DOTS:
            dot = self.create_random_dot()
        return dot

    def update_swallowed_players(self, player_number):

        player_data = self.get_player_data(player_number)
        other_players = self.get_other_live_players(player_number)
        eaten_players = [other_player_data for other_player_data in other_players if
                             CollisionUtils.check_collision(player_data.coord, player_data.radius,
                                                            other_player_data.coord, other_player_data.radius)]

        other_players = self.get_other_live_players(player_number)
        eaten_by_players = [other_player_data for other_player_data in other_players
                                        if CollisionUtils.check_collision(other_player_data.coord,
                                                                          other_player_data.radius,
                                                                          player_data.coord, player_data.radius)]

        for eaten_player in eaten_players:
            eaten_player.is_alive = False
            self.add_player_swallowed_points(player_data, eaten_player)

        for player in eaten_by_players:
            self.add_player_swallowed_points(player, player_data)
            player_data.is_alive = False

        return eaten_players, eaten_by_players

    def get_score_rating(self):
        return sorted(self.get_players_data().items(), key=lambda x: x[1].score)

    def has_winner(self):
        alive_players = self.get_live_players()
        if len(alive_players) == 1 and self.is_ready():
            return True, alive_players[0]
        else:
            return False, None

    def add_player_swallowed_points(self, player_data, eaten_player):
        player_data.radius *= (eaten_player.radius / 12)
        player_data.score += max(eaten_player.score, MIN_EATEN_PLAYER_SCORE)

    def find_swallowed_dots(self, player_number):
        player_data = self.get_player_data(player_number)
        swallowed_dots = [dot for dot in self.dots.values() if CollisionUtils.check_collision(player_data.coord, player_data.radius,
                                                                                              dot.coord, dot.radius)]
        return swallowed_dots

    def remove_dots(self, dots_to_remove):
        for dot in dots_to_remove:
            del self.dots[dot.id]

    def add_dots_points(self, player_number, swallowed_dots):
        points = DotUtils.get_points_sum(swallowed_dots)
        increase = DotUtils.get_increase_sum(swallowed_dots)

        player_data = self.get_player_data(player_number)
        player_data.radius += increase
        player_data.score += points
        return player_data

    def update_game_state(self, player_number):
        modified_players = []
        if not self.is_connected(player_number):
            return [self.get_player_data(player_number)], []

        player_data = self.get_player_data(player_number)

        swallowed_dots = self.find_swallowed_dots(player_number)
        if len(swallowed_dots) > 0:
            self.add_dots_points(player_number, swallowed_dots)
            self.remove_dots(swallowed_dots)

        eaten_players, eaten_by_players = self.update_swallowed_players(player_number)

        modified_players += eaten_players
        modified_players += eaten_by_players

        if len(swallowed_dots) > 0 or len(modified_players) > 0:
            modified_players.append(player_data)

        return modified_players, DotUtils.get_ids(swallowed_dots)



