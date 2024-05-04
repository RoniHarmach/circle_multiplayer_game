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
    def get_points_sum(dots):
        return sum(dot.points for dot in dots)

    @staticmethod
    def get_ids(dots):
        return [dot.id for dot in dots]