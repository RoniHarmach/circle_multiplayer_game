import struct

import pygame, threading, socket, sys, pickle
from game_protocol import GameProtocol
from mouse_move_handler import MouseMoveHandler
from player import Player
from protocol_codes import ProtocolCodes
from user_event_message import UserEventMessage
from queue import Queue


WIDTH, HEIGHT = 800, 600
connected = False
player: Player = None
game_started = False
pygame.init()

def create_player(bdata):
    global player
    deserialized_player = pickle.loads(bdata)
    player = Player(deserialized_player)


def load_entry_screen(screen):
    background_image_path = "sprite/entry_background.jpeg"
    background_image = pygame.image.load(background_image_path).convert()
    screen.blit(background_image, (0, 0))
    pygame.display.flip()

def handle_create_player_request(bdata, screen):
    print("handle create player req")
    create_player(bdata)
    load_entry_screen(screen)

def start_game(screen):
    global game_started
    print("Starting game")
    redraw_screen(screen)
    game_started = True


def redraw_screen(screen):
    global player
    screen.fill(pygame.Color("white"))
    player.draw(screen)
    pygame.display.flip()


def handle_user_events(message: UserEventMessage, screen):
    if message.code == ProtocolCodes.CREATE_PLAYER:
        handle_create_player_request(message.data, screen)
    elif message.code == ProtocolCodes.START_GAME:
        start_game(screen)


def client_window_handler(client_notification_queue):
    running = True

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(pygame.Color("white"))
    pygame.display.flip()
    mouseMoveHandler = MouseMoveHandler()
    mouse_pos = None
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEMOTION and game_started:
                print("Mouse motion detected:", event.pos)
                mouse_pos = event.pos

            elif event.type == pygame.USEREVENT:
                handle_user_events(event.message, screen)

        if mouse_pos is not None:
            if mouseMoveHandler.handle_movement(player, mouse_pos):
                redraw_screen(screen)
                client_notification_queue.put(UserEventMessage(ProtocolCodes.PLAYER_MOVED, struct.pack('ii', *player.player_data.coord)))
            else:
                mouse_pos = None

        pygame.time.Clock().tick(40)


def handle_server_messages(server_socket):
    global connected
    while connected:
        code, bdata = GameProtocol.read_data(server_socket)
        # send server message as user event
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=UserEventMessage(code, bdata)))

        if bdata == b'' and code != ProtocolCodes.START_GAME:
            print('Seems server disconnected abnormally')
            break


def open_client_socket(ip):
    global connected
    sock = socket.socket()
    port = 6060
    try:
        sock.connect((ip, port))
        print(f'Connect succeeded {ip}:{port}')
        connected = True
        return sock
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
        return None


def handle_client_messages(server_socket, client_notification_queue):
    while True:
        user_message = client_notification_queue.get()
        GameProtocol.send_data(server_socket, user_message.code, user_message.data)


def main(server_ip):
    client_notification_queue = Queue()
    server_socket = open_client_socket(server_ip)
    window_thread = threading.Thread(target=client_window_handler, args=(client_notification_queue,))
    window_thread.start()
    message_thread = threading.Thread(target=handle_server_messages, args=(server_socket,))
    message_thread.start()
    server_notifications_thread = threading.Thread(target=handle_client_messages, args=(server_socket, client_notification_queue,))
    server_notifications_thread.start()
    window_thread.join()
    server_socket.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')