# Data of the player which is transferred between client and server.
class PlayerData:

    def __init__(self, coord, color, player_number, radius=15):
        self.coord = coord
        self.color = color
        self.radius = radius
        self.player_number = player_number
