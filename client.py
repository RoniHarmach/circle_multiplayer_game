import socket
import sys
import pickle
import pygame
from game_protocol import GameProtocol
from protocol_codes import ProtocolCodes
from player_utils import PlayerUtils
from player import Player
from player_data import PlayerData

WIDTH, HEIGHT = 800, 600
pygame.init()


def open_client_socket(ip):
    connected = False
    sock = socket.socket()
    port = 5151
    try:
        sock.connect((ip, port))
        print(f'Connect succeeded {ip}:{port}')
        connected = True
        return sock, connected
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
    return sock, connected


def handle_create_player(bdata):
    deserialized_player = pickle.loads(bdata)
    player = Player(deserialized_player)
    pygame.init()
    running = True
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(pygame.Color("white"))
        player.draw(screen)
        pygame.display.update()
    pygame.quit()





def handle_message(code, bdata):
    if code == ProtocolCodes.CREATE_PLAYER:
        print("handling create player")
        handle_create_player(bdata)



def main(ip):
    sock, connected = open_client_socket(ip)
    pygame.init()
    while connected:
        code, byte_data = GameProtocol.read_data(sock)
        handle_message(code, byte_data)
        if byte_data == b'':
            print('Seems server disconnected abnormal')
            break

        print("d")
    print('Bye')
    sock.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')
