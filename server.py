import socket, threading, pickle, pygame
from queue import Queue
from game_event import GameEvent
from game_messages import GameInitMessage, GameStateChangeMessage, PlayerMovementMessage
from game_manager import GameManager
from player_data import PlayerData
from game_protocol import GameProtocol
from player_state import PlayerState
from protocol_codes import ProtocolCodes
from server_event_types import ServerEventType

PLAYERS_NUMBER = 3
all_to_die = False  # global
player_colors = [pygame.Color("red"), pygame.Color("green"), pygame.Color("blue") ]
player_initial_coords = [(500, 210), (130, 50), (100, 120)]
game_manager = GameManager(PLAYERS_NUMBER)

# 1. don't send client event if player is dead
# 2. check if a player eats another player then his score and radius increase
# 3. the eaten player get a message that he is dead
# 4. adding score bored
# 5. create random points and make sure you dont make them in players entery place
# 6. add point once in a while and send in game change new event of add point
# for 6 i can add new thread that every x time (time sleep) add a point (random place)

def open_server_socket():
    srv_sock = socket.socket()
    port = 6060
    srv_sock.bind(('0.0.0.0', port))
    srv_sock.listen(2)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return srv_sock


def create_player_data(player_number):
    return PlayerData(player_initial_coords[player_number - 1], player_colors[player_number - 1], player_number)


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
        # player_data = game_manager.add_dots_points(player_number, removed_dots)
        change_state_message = GameStateChangeMessage(players=modified_players, removed_dots=removed_dots)
        serialized_message = pickle.dumps(change_state_message)
        notify_all_players(serialized_message, ProtocolCodes.GAME_STATE_CHANGE)
    else:
        serialized_message = pickle.dumps(PlayerMovementMessage(player_number=player_number, coords=coord))
        notify_other_players(serialized_message, ProtocolCodes.PLAYER_MOVED, player_number)


def handle_server_messages(server_notification_queue):
    while True:
        event = server_notification_queue.get()
        if event.code == ServerEventType.CREATE_PLAYER_REQUEST:
            create_player(event.player_number)
            if game_manager.is_all_players_joined():
                initialize_game()
        elif event.code == ServerEventType.PLAYER_READY:
            handle_player_ready_message(event.player_number)
        elif event.code == ServerEventType.PLAYER_MOVED:
            handle_player_movement(event.player_number, event.message)


def handle_client(sock, player_number, server_notification_queue):
    global all_to_die
    finish = False
    create_player_state(client_socket=sock, player_number=player_number)
    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        code, message = GameProtocol.read_data(sock)
        if code == ProtocolCodes.CREATE_PLAYER_REQUEST:
            client_event = GameEvent(code=ServerEventType.CREATE_PLAYER_REQUEST, player_number=player_number)
            server_notification_queue.put(client_event)
        elif code == ProtocolCodes.PLAYER_READY:
            client_event = GameEvent(code=ServerEventType.PLAYER_READY, player_number=player_number)
            server_notification_queue.put(client_event)
        elif code == ProtocolCodes.PLAYER_MOVED:
            client_event = GameEvent(code=ServerEventType.PLAYER_MOVED, message=message, player_number=player_number)
            server_notification_queue.put(client_event)
        elif code == ProtocolCodes.PLAYER_READY:
            client_event = GameEvent(code=ServerEventType.PLAYER_READY, player_number=player_number)
            server_notification_queue.put(client_event)


def create_player_state_message(player_number):
    return  pickle.dumps(game_manager.get_player_data(player_number))


def get_player_position_message(player_number):
    return pickle.dumps(player_number, game_manager.get_player_position(player_number))


def notify_create_player(player_number):
    serialized_player_data = create_player_state_message(player_number)
    notify_player(player_number, serialized_player_data, ProtocolCodes.CREATE_PLAYER)


def notify_player_movement(notified_player_number, player_changed_number):
    serialized_player_data = get_player_position_message(player_changed_number)
    notify_player(notified_player_number, serialized_player_data, ProtocolCodes.PLAYER_MOVED)


def notify_all_players(message, code):
    for player_number in game_manager.get_all_player_numbers():
        notify_player(player_number, message, code)


def notify_other_players(message, code, excluded_player_number):
    for player_number in game_manager.get_all_player_numbers():
        if player_number != excluded_player_number:
            notify_player(player_number, message, code)


def notify_player(player_number, message, code):
    client_socket = game_manager.get_client_socket(player_number)
    print(f"notifying {player_number} on {code}")
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
    for player_number in game_manager.get_all_player_numbers():
        other_players = game_manager.get_other_players_data(player_number)
        player_data = game_manager.get_player_data(player_number)
        message = GameInitMessage(player_data=player_data, other_players=other_players, dots=dots)
        serialized_message = pickle.dumps(message)
        notify_player(player_number, serialized_message, ProtocolCodes.GAME_INIT)


def accept_clients(srv_sock):
    threads = []
    server_notification_queue = Queue()

    server_notifications_thread = threading.Thread(target=handle_server_messages, args=(server_notification_queue,))
    server_notifications_thread.start()

    player_number = 1
    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()  # accepts an incoming connection request from a TCP client.
        # (clientConnection, clientAddress) = serverSocket.accept()

        t = threading.Thread(target=handle_client, args=(cli_sock, player_number, server_notification_queue))
        t.start()  # אומרת לתוכנית לפתוח את הטרד ולהריץ את ההנדל קליינט
        player_number += 1
        i += 1
        threads.append(t)  ## מוסיפה למערך של הטרדים

        if i > 100000000:  # for tests change it to 4
            print('\nMain thread: going down for maintenance')
            break

    all_to_die = True  # מדליקים את הדגל שיגרום לטרדים להפסיק
    print('Main thread: waiting to all clints to die')
    for t in threads:  #
        print("Joining thread " + t.getName())
        # לכל טרד
        t.join()  # עוצר את הטרייד מיין עד ש הטי סוגר את עצמו
    srv_sock.close()  # סוגרים את הסוקט הראשי של השרת
    print('Bye ..')


def main():
    global all_to_die
    srv_sock = open_server_socket()
    accept_clients(srv_sock)


if __name__ == '__main__':
    main()