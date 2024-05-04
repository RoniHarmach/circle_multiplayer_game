import pygame, threading, socket, sys, pickle, struct
from typing import Dict

from dot import Dot
from dot_data import DotData
from game_protocol import GameProtocol
from mouse_move_handler import MouseMoveHandler
from player import Player
from protocol_codes import ProtocolCodes
from user_event_message import UserEventMessage
from queue import Queue

other_players: Dict[int, Player] = {}
dots: Dict[int, Dot] = None
WIDTH, HEIGHT = 800, 600
connected = False
game_started = False
pygame.init()
player: Player = None


def remove_dots(dot_ids):
    for key in dot_ids:
        if key in dots:
            del dots[key]


def load_entry_screen(screen):
    background_image_path = "sprite/entry_background.jpeg"
    background_image = pygame.image.load(background_image_path).convert()
    screen.blit(background_image, (0, 0))
    pygame.display.flip()


def start_game(screen):
    global game_started
    print("Starting game")
    redraw_screen(screen)
    game_started = True


def get_live_players():
    return [other_player for other_player in other_players.values() if other_player.player_data.is_alive]


def redraw_screen(screen):
    global player
    screen.fill(pygame.Color("white"))
    for other_player in get_live_players():
        other_player.draw(screen)
    for dot in dots.values():
        dot.draw(screen)
    if player.player_data.is_alive:
        player.draw(screen)
    pygame.display.flip()


def handle_other_players_movements(bdata, screen):
    deserialized_player_position = pickle.loads(bdata)
    other_player = other_players[deserialized_player_position.player_number]
    other_player.player_data.coord = deserialized_player_position.coords
    redraw_screen(screen)


def initialize_game(data, screen, client_notification_queue):
    global player, dots, other_players
    message = pickle.loads(data)
    dots = {key: Dot(dot_data) for key, dot_data in message.dots.items()}
    player = Player(message.player_data)
    other_players = {key: Player(player_data) for key, player_data in message.other_players.items()}
    client_notification_queue.put(UserEventMessage(ProtocolCodes.PLAYER_READY, b''))


def update_player_state(player_data):
    if player_data.player_number == player.player_data.player_number:
        player.player_data = player_data
    else:
        print(f"updating player {player_data.player_number}: {player_data.is_alive}")
        other_players[player_data.player_number].player_data = player_data


def update_players_states(players):
    if players is not None:
        for player_data in players:
            update_player_state(player_data)


def handle_game_state_change(data, screen):
    message = pickle.loads(data)
    update_players_states(message.players)
    remove_dots(message.removed_dots)
    redraw_screen(screen)


def handle_user_events(message: UserEventMessage, screen, client_notification_queue):
    if message.code == ProtocolCodes.GAME_INIT:
        initialize_game(message.data, screen, client_notification_queue)
    elif message.code == ProtocolCodes.LOAD_ENTRY_SCREEN:
        load_entry_screen(screen)
    elif message.code == ProtocolCodes.START_GAME:
        start_game(screen)
    elif message.code == ProtocolCodes.PLAYER_MOVED:
        handle_other_players_movements(message.data, screen)
    elif message.code == ProtocolCodes.GAME_STATE_CHANGE:
        handle_game_state_change(message.data, screen)


def client_window_handler(client_notification_queue):
    running = True

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(pygame.Color("white"))
    pygame.display.flip()
    mouse_move_handler = MouseMoveHandler()
    mouse_pos = None
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEMOTION and game_started:
                mouse_pos = event.pos

            elif event.type == pygame.USEREVENT:
                handle_user_events(event.message, screen, client_notification_queue)

        if mouse_pos is not None:
            if mouse_move_handler.handle_movement(player, mouse_pos):
                redraw_screen(screen)
                client_notification_queue.put(UserEventMessage(ProtocolCodes.PLAYER_MOVED, pickle.dumps(player.player_data.coord)))
            else:
                mouse_pos = None

        pygame.time.Clock().tick(40)


def handle_server_messages(server_socket):
    global connected
    while connected:
        code, bdata = GameProtocol.read_data(server_socket)
        # send server message as user event
        #print(f"got message with code {code} from server")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=UserEventMessage(code, bdata)))

        if bdata == b'' and code not in [ProtocolCodes.START_GAME, ProtocolCodes.GAME_INIT]:
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


def create_client_request(server_socket):
    GameProtocol.send_data(server_socket, ProtocolCodes.CREATE_PLAYER_REQUEST, b'')


def main(server_ip):
    client_notification_queue = Queue()
    server_socket = open_client_socket(server_ip)
    window_thread = threading.Thread(target=client_window_handler, args=(client_notification_queue,))
    window_thread.start()
    message_thread = threading.Thread(target=handle_server_messages, args=(server_socket,))
    message_thread.start()
    server_notifications_thread = threading.Thread(target=handle_client_messages, args=(server_socket, client_notification_queue,))
    server_notifications_thread.start()
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=UserEventMessage(code=ProtocolCodes.LOAD_ENTRY_SCREEN, data=b'')))

    create_client_request(server_socket)

    window_thread.join()
    server_socket.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')