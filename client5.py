import pygame, threading, socket, sys, pickle
from typing import Dict
from dot import Dot
from game_constants import *
from game_over import GameOver
from game_protocol import *
from mouse_move_handler import MouseMoveHandler
from player import Player
from protocol_codes import ProtocolCodes
from score_board import ScoreBoard
from user_event_message import UserEventMessage
from queue import Queue

other_players: Dict[int, Player] = {}
dots: Dict[int, Dot] = None
connected = False
is_active_player = False
pygame.init()
player: Player = None
score_board = ScoreBoard()
game_over = GameOver()
running = False
game_finished = False


def remove_dots(dot_ids):
    if dot_ids is None:
        return
    for key in dot_ids:
        if key in dots:
            del dots[key]


def load_entry_screen(screen):
    background_image_path = "sprite/entry_background.jpeg"
    background_image = pygame.image.load(background_image_path).convert()
    screen.blit(background_image, (0, 0))
    pygame.display.flip()


def start_game(screen):
    global is_active_player
    redraw_screen(screen)
    is_active_player = True


def get_live_players():
    return [other_player for other_player in other_players.values() if other_player.player_data.is_alive]


def get_other_players_data():
    return [other_player.player_data for other_player in other_players.values()]


def redraw_screen(screen):
    global player, score_board, other_players
    pygame.display.set_caption("Holes Game - Roni Harmach")
    screen.fill(pygame.Color("white"))
    for other_player in get_live_players():
        other_player.draw(screen)
    for dot in dots.values():
        dot.draw(screen)
    if player.player_data.is_alive:
        player.draw(screen)
    else:
        game_over.draw(screen)
    score_board.draw(screen)
    pygame.display.flip()


def handle_other_players_movements(bdata, screen):
    deserialized_player_position = pickle.loads(bdata)
    other_player = other_players[deserialized_player_position.player_number]
    other_player.player_data.coord = deserialized_player_position.coords
    redraw_screen(screen)


def initialize_game(data, client_notification_queue):
    global player, dots, other_players
    message = pickle.loads(data)
    dots = {key: Dot(dot_data) for key, dot_data in message.dots.items()}
    player = Player(player_data=message.player_data)
    other_players = {key: Player(player_data) for key, player_data in message.other_players.items()}
    score_board.update_state(player.player_data, get_other_players_data())
    client_notification_queue.put(UserEventMessage(ProtocolCodes.PLAYER_READY, b''))


def update_player_state(player_data):
    global is_active_player

    if player_data.player_number == player.player_data.player_number:
        player.player_data = player_data
        is_active_player = player_data.is_alive
    else:
        other_players[player_data.player_number].player_data = player_data


def update_players_states(players):
    if players is not None:
        for player_data in players:
            update_player_state(player_data)


def add_dot(added_dot):
    if added_dot is not None:
        dots[added_dot.id] = Dot(added_dot)


def handle_game_state_change(data, screen):
    global player
    message = pickle.loads(data)
    update_players_states(message.players)
    remove_dots(message.removed_dots)
    add_dot(message.added_dot)
    if message.players is not None and len(message.players) > 0:
        score_board.update_state(player.player_data, get_other_players_data())
    redraw_screen(screen)


def load_podium_screen(message, screen):
    pygame.display.set_caption("Holes Game - Roni Harmach")
    deserialized_players_rating = pickle.loads(message)
    background_image_path = "sprite/podium3.png"
    background_image = pygame.image.load(background_image_path).convert()
    font = pygame.font.Font(None, 36)
    placements = {3: [530, 230],
                  2: [335, 288],
                  1: [730, 318]
                  }
    screen.blit(background_image, (0, 0))

    for i in range(3):
        deserialized_players_rating.sorted_players[i][1].radius = 40
        deserialized_players_rating.sorted_players[i][1].coord = placements[i+1]
        player = Player(player_data=deserialized_players_rating.sorted_players[i][1])
        player.draw(screen)
        text_surface = font.render(f"score: {str(player.player_data.score)}", True, pygame.Color("black"))
        text_rect = text_surface.get_rect()
        text_rect.center = (deserialized_players_rating.sorted_players[i][1].coord[0],
                            deserialized_players_rating.sorted_players[i][1].coord[1] - 70)
        screen.blit(text_surface, text_rect)

    pygame.display.flip()


def handle_user_events(message: UserEventMessage, screen, client_notification_queue):
    global running, game_finished
    if message.code == ProtocolCodes.GAME_INIT:
        initialize_game(message.data, client_notification_queue)
    elif message.code == ProtocolCodes.LOAD_ENTRY_SCREEN:
        load_entry_screen(screen)
    elif message.code == ProtocolCodes.START_GAME:
        start_game(screen)
    elif message.code == ProtocolCodes.PLAYER_MOVED:
        handle_other_players_movements(message.data, screen)
    elif message.code == ProtocolCodes.GAME_STATE_CHANGE:
        handle_game_state_change(message.data, screen)
    elif message.code == ProtocolCodes.GAME_RESULTS:
        load_podium_screen(message.data, screen)
        game_finished = True
    # elif message.code == ProtocolCodes.DISCONNECT_FROM_SERVER:
    #     client_notification_queue.put(UserEventMessage(ProtocolCodes.CLIENT_DISCONNECTED, b''))


def client_window_handler(client_notification_queue):
    global player, running, is_active_player, game_finished
    running = True
    pygame.display.set_caption("Holes Game - Roni Harmach")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(pygame.Color("white"))
    pygame.display.flip()
    mouse_move_handler = MouseMoveHandler()
    mouse_pos = None
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEMOTION and is_active_player and not game_finished:
                mouse_pos = event.pos

            elif event.type == pygame.USEREVENT:
                handle_user_events(event.message, screen, client_notification_queue)
        if mouse_pos is not None and not game_finished:
            if mouse_move_handler.handle_movement(player, mouse_pos):
                redraw_screen(screen)
                client_notification_queue.put(UserEventMessage(ProtocolCodes.PLAYER_MOVED, pickle.dumps(player.player_data.coord)))
            else:
                mouse_pos = None

        pygame.time.Clock().tick(PYGAME_CLOCK_TICK)


def handle_server_messages(server_socket):
    global connected
    while connected:
        try:
            code, bdata = GameProtocol.read_data(server_socket)

            if bdata == b'' and code not in [ProtocolCodes.START_GAME, ProtocolCodes.GAME_INIT]:
                print('Seems server disconnected abnormally')
                break

            pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=UserEventMessage(code, bdata)))

            if code == ProtocolCodes.GAME_RESULTS:
                connected = False
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, message=UserEventMessage(ProtocolCodes.CLIENT_DISCONNECTED, bdata)))
                server_socket.close()
        except GameProtocolError as ex:
            print(f"Protocol error occurred: {ex}")





def open_client_socket(ip):
    global connected
    sock = socket.socket()
    try:
        sock.connect((ip, PORT))
        connected = True
        return sock
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{PORT}')
        return None


def handle_client_messages(server_socket, client_notification_queue):
    read_client_messages = True
    while read_client_messages:
        user_message = client_notification_queue.get()
        GameProtocol.send_data(server_socket, user_message.code, user_message.data)
        if user_message.code == ProtocolCodes.CLIENT_DISCONNECTED:
            GameProtocol.send_data(server_socket, ProtocolCodes.CLIENT_DISCONNECTED, b'')
            read_client_messages = False
    server_socket.close()


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
        main(HOST)
        #main('0.0.0.0')
        #main('10.68.121.10')
