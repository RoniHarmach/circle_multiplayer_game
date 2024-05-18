import socket, threading, pickle
import time
from queue import Queue

from game_constants import *
from game_event import GameEvent
from game_messages import GameInitMessage, GameStateChangeMessage, PlayerMovementMessage, GameResults
from game_manager import GameManager
from player_data import PlayerData
from game_protocol import *
from player_state import PlayerState
from protocol_codes import ProtocolCodes
from server_event_types import ServerEventType

all_to_die = False
game_manager = GameManager()


def open_server_socket():
    srv_sock = socket.socket()
    srv_sock.bind(('0.0.0.0', PORT))
    srv_sock.listen(2)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return srv_sock


def create_player_data(player_number):
    return PlayerData(PLAYER_INITIAL_COORDS[player_number - 1], PLAYER_COLORS[player_number - 1], player_number)


def logtcp(dir, tid, byte_data):

    if dir == 'sent':
        print(f'{tid} S LOG:Sent     >>> {byte_data}')
    else:
        print(f'{tid} S LOG:Recieved <<< {byte_data}')


def handle_player_ready_message(player_number):
    game_manager.set_player_ready(player_number)
    if game_manager.is_ready():
        notify_all_players(b'', ProtocolCodes.START_GAME)


def handle_player_movement(player_number, message):
    coord = pickle.loads(message)
    game_manager.update_position(player_number, coord)
    modified_players, removed_dots = game_manager.update_game_state(player_number)

    if len(modified_players) > 0 or len(removed_dots) > 0:
        change_state_message = GameStateChangeMessage(players=modified_players, removed_dots=removed_dots)
        serialized_message = pickle.dumps(change_state_message)
        notify_all_players(serialized_message, ProtocolCodes.GAME_STATE_CHANGE)
    else:
        serialized_message = pickle.dumps(PlayerMovementMessage(player_number=player_number, coords=coord))
        notify_other_players(serialized_message, ProtocolCodes.PLAYER_MOVED, player_number)


def handle_add_dot(dot_id):
    change_state_message = GameStateChangeMessage(added_dot=game_manager.get_dot_data(dot_id), players=[])
    serialized_message = pickle.dumps(change_state_message)
    notify_all_players(serialized_message, ProtocolCodes.GAME_STATE_CHANGE)


def handle_server_disconnection():
    notify_all_players(b'', ProtocolCodes.SERVER_DISCONNECT)


def notify_on_game_results():
    change_state_message = GameResults(sorted_players=game_manager.get_score_rating())
    serialized_message = pickle.dumps(change_state_message)
    notify_all_players(serialized_message, ProtocolCodes.GAME_RESULTS)


# def handle_end_game():
#     # global all_to_die
#
#     has_winner, winner = game_manager.has_winner()
#     if has_winner:
#         notify_on_game_results()
#
#         # all_to_die = True
#     return has_winner


def handle_client_disconnection(player_number):
    game_manager.set_player_is_alive(player_number, False)
    game_manager.set_client_disconnected(player_number)
    modified_players, removed_dots = game_manager.update_game_state(player_number)
    change_state_message = GameStateChangeMessage(players=modified_players)
    serialized_message = pickle.dumps(change_state_message)
    notify_all_players(serialized_message, ProtocolCodes.GAME_STATE_CHANGE)


def check_for_game_end():
    has_winner, winner = game_manager.has_winner()
    if has_winner:
        notify_on_game_results()

    return not has_winner


def handle_server_messages(server_notification_queue):
    running = True
    while running:
        event = server_notification_queue.get()
        if event.code == ServerEventType.CREATE_PLAYER_REQUEST:
            create_player(event.player_number)
            if game_manager.is_all_players_joined():
                initialize_game()
        elif event.code == ServerEventType.PLAYER_READY:
            handle_player_ready_message(event.player_number)
        elif event.code == ServerEventType.PLAYER_MOVED:
            handle_player_movement(event.player_number, event.message)
        elif event.code == ServerEventType.ADD_DOT:
            handle_add_dot(event.message)
        elif event.code == ServerEventType.SERVER_DISCONNECT:
            handle_server_disconnection()
        elif event.code == ServerEventType.CLIENT_CONNECTION_CLOSED:
            handle_client_disconnection(event.player_number)
        elif event.code == ServerEventType.STOP_SERVER_EVENTS:
            break
        running = check_for_game_end()
    print("exit handle_server_events")

def handle_client(sock, player_number, server_notification_queue):
    global all_to_die
    finish = False
    create_player_state(client_socket=sock, player_number=player_number)

    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        try:
            code, message = GameProtocol.read_data(sock)
            if code == ProtocolCodes.CLIENT_DISCONNECTED:
                client_event = GameEvent(code=ServerEventType.CLIENT_CONNECTION_CLOSED, player_number=player_number)
                server_notification_queue.put(client_event)
                finish = True
            if code == ProtocolCodes.CREATE_PLAYER_REQUEST:
                client_event = GameEvent(code=ServerEventType.CREATE_PLAYER_REQUEST, player_number=player_number)
                server_notification_queue.put(client_event)
            elif code == ProtocolCodes.PLAYER_READY:
                client_event = GameEvent(code=ServerEventType.PLAYER_READY, player_number=player_number)
                server_notification_queue.put(client_event)
            elif code == ProtocolCodes.PLAYER_MOVED:
                client_event = GameEvent(code=ServerEventType.PLAYER_MOVED, message=message, player_number=player_number)
                server_notification_queue.put(client_event)
        except GameProtocolError as ex:
            print(f"Protocol error occurred: {ex}")
    ### game_manager.set_player_is_alive(player_number, False)
    sock.close()


def create_player_state_message(player_number):
    return pickle.dumps(game_manager.get_player_data(player_number))


def get_player_position_message(player_number):
    return pickle.dumps(player_number, game_manager.get_player_position(player_number))


def notify_create_player(player_number):
    serialized_player_data = create_player_state_message(player_number)
    notify_player(player_number, serialized_player_data, ProtocolCodes.CREATE_PLAYER)


def notify_player_movement(notified_player_number, player_changed_number):
    serialized_player_data = get_player_position_message(player_changed_number)
    notify_player(notified_player_number, serialized_player_data, ProtocolCodes.PLAYER_MOVED)


def notify_all_players(message, code):
    for player_number in game_manager.get_all_connected_player_numbers():
        notify_player(player_number, message, code)


def notify_other_players(message, code, excluded_player_number):
    for player_number in game_manager.get_all_connected_player_numbers():
        if player_number != excluded_player_number:
            notify_player(player_number, message, code)


def notify_player(player_number, message, code):
    client_socket = game_manager.get_client_socket(player_number)
    GameProtocol.send_data(client_socket, code, message)


def create_player_state(client_socket, player_number):
    global game_manager

    state = PlayerState(client_socket=client_socket)
    game_manager.add_player_state(player_number, state)


def create_player(player_number):
    global game_manager
    player_data = create_player_data(player_number)
    game_manager.add_player_data(player_number, player_data)


def initialize_game():
    dots = game_manager.initialize_dots()
    for player_number in game_manager.get_all_connected_player_numbers():
        other_players = game_manager.get_other_players_data(player_number)
        player_data = game_manager.get_player_data(player_number)
        message = GameInitMessage(player_data=player_data, other_players=other_players, dots=dots)
        serialized_message = pickle.dumps(message)
        notify_player(player_number, serialized_message, ProtocolCodes.GAME_INIT)


def dots_creator(server_notification_queue):
    global all_to_die

    while not all_to_die:
        time.sleep(2)

        if game_manager.is_ready():
            dot = game_manager.create_missing_dot()
            if dot is not None:
                server_notification_queue.put(GameEvent(code=ServerEventType.ADD_DOT, message=dot.id))


def accept_clients(srv_sock):
    global all_to_die

    threads = []
    server_notification_queue = Queue()

    server_notifications_thread = threading.Thread(target=handle_server_messages, args=(server_notification_queue,))
    server_notifications_thread.start()
    server_dots_thread = threading.Thread(target=dots_creator, args=(server_notification_queue,))
    server_dots_thread.start()

    player_number = 1
    i = 1
    try:
        srv_sock.settimeout(30)
        while i < 4:
            print('\nMain thread: before accepting ...')
            cli_sock, addr = srv_sock.accept()  # accepts an incoming connection request from a TCP client.
            t = threading.Thread(target=handle_client, args=(cli_sock, player_number, server_notification_queue))
            t.start()  # אומרת לתוכנית לפתוח את הטרד ולהריץ את ההנדל קליינט
            player_number += 1
            i += 1
            threads.append(t)  ## מוסיפה למערך של הטרדים
    except socket.timeout:
        print("got timeout")
        all_to_die = True
        close_event = GameEvent(code=ServerEventType.SERVER_DISCONNECT)
        server_notification_queue.put(close_event)
    finally:

        for t in threads:  #
            # לכל טרד
            t.join()  # עוצר את הטרייד מיין עד ש הטי סוגר את עצמו
            print("closed thread " + t.getName())

        close_server_events = GameEvent(code=ServerEventType.STOP_SERVER_EVENTS)
        server_notification_queue.put(close_server_events)
        all_to_die = True
        server_notifications_thread.join()
        srv_sock.close()


def main():
    global all_to_die
    srv_sock = open_server_socket()
    accept_clients(srv_sock)


if __name__ == '__main__':
    main()