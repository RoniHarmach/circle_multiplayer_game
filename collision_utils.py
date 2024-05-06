import math


class CollisionUtils:

    @staticmethod
    def check_collision(coord1, radius1, coord2, radius2):
        if radius1 < radius2:
            return False
        distance = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
        if distance <= radius1 - radius2:
            return True
        else:
            return False

    @staticmethod
    def check_new_dot_collision(coord1, radius1, coord2, radius2):
        distance = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
        return distance <= (radius1 + radius2)
