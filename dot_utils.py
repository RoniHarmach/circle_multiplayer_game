import random
from dot_data import DotData
from game_constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCORE_BOARD_HEIGHT

MIN_DISTANCE_FROM_BORDERS = 5


class DotUtils:
    @staticmethod
    def create_random_dot(id):
        small = {"radius": 4, "color": "red", "points": 2, "increase": 1}
        medium = {"radius": 6, "color": "green", "points": 4, "increase": 2}
        large = {"radius": 9, "color": "blue", "points": 8, "increase": 4}
        xlarge = {"radius": 15, "color": "orange", "points": 15, "increase": 6}
        xxlarge = {"radius": 18, "color": "yellow", "points": 25, "increase": 7}

        random_percentage = random.randint(1, 100)
        if random_percentage < 50:
            parameters = small
        elif random_percentage < 70:
            parameters = medium
        elif random_percentage < 87:
            parameters = large
        elif random_percentage < 95:
            parameters = xlarge
        else:
            parameters = xxlarge
        dot_radius = parameters["radius"]
        random_x = random.randint(dot_radius + MIN_DISTANCE_FROM_BORDERS, SCREEN_WIDTH - dot_radius - MIN_DISTANCE_FROM_BORDERS)
        random_y = random.randint(dot_radius + SCORE_BOARD_HEIGHT + MIN_DISTANCE_FROM_BORDERS, SCREEN_HEIGHT - dot_radius - MIN_DISTANCE_FROM_BORDERS)

        return DotData(id=id, coord=(random_x, random_y), color=parameters["color"],radius=dot_radius,
                       points=parameters["points"], increase=parameters["increase"])

    @staticmethod
    def get_points_sum(dots):
        return sum(dot.points for dot in dots)

    @staticmethod
    def get_increase_sum(dots):
        return sum(dot.increase for dot in dots)

    @staticmethod
    def get_ids(dots):
        return [dot.id for dot in dots]