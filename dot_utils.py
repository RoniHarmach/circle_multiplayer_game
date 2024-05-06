import random
from dot_data import DotData


class DotUtils:
    @staticmethod
    def create_dots():
        return {
            1: DotData(id=1, coord=(60, 130), color ="blue", radius=10, points=4),
            2: DotData(id=2, coord=(60, 168), color ="blue", radius=10, points=4),
            3: DotData(id=3, coord=(459, 234), color="blue", radius=10, points=4),
            4: DotData(id=4, coord=(340, 90), color="red", radius=18, points=6),
            5: DotData(id=5, coord=(60, 400), color="red", radius=18, points=6)
        }

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
        random_x = random.randint(int(dot_radius/2), 800-int(dot_radius/2))
        random_y = random.randint(int(dot_radius/2), 600-int(dot_radius/2))

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