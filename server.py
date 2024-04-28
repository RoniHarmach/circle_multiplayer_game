import socket, threading, pickle, pygame, time
from queue import Queue
from typing import Dict

from game_event import GameEvent
from player_data import PlayerData
from game_protocol import GameProtocol
from player_state import PlayerState
from protocol_codes import ProtocolCodes


players_states: Dict[int, PlayerState] = {}

all_to_die = False  # global

player_colors = [pygame.Color("red"), pygame.Color("green"), pygame.Color("blue") ]
player_initial_coords = [(500, 210), (130, 50), (100, 120)]


def open_server_socket():
    srv_sock = socket.socket()
    port = 6060
    srv_sock.bind(('0.0.0.0', port))
    srv_sock.listen(2)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return srv_sock


def create_player_data(player_number):
    player_data = PlayerData(player_initial_coords[player_number - 1], player_colors[player_number - 1], player_number)
    return player_data


def logtcp(dir, tid, byte_data):

    if dir == 'sent':
        print(f'{tid} S LOG:Sent     >>> {byte_data}')
    else:
        print(f'{tid} S LOG:Recieved <<< {byte_data}')


def handle_server_messages(server_notification_queue):
    while True:
        event = server_notification_queue.get()
        if event.code == ProtocolCodes.CREATE_PLAYER_REQUEST:
            create_player(event.player_number)
            notify_create_player(event.player_number)
            for player, player_state in players_states.items():
                if player != event.player_number:
                    notify_player_state(player, event.player_number)
                    notify_player_state(event.player_number, player)
        elif event.code == ProtocolCodes.START_GAME:

            for player in players_states.keys():
                notify_start_game(player)


def handle_client(sock, player_number, server_notification_queue):
    global all_to_die
    finish = False
    create_player_state(client_socket=sock, player_number=player_number)
    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        code, message = GameProtocol.read_data(sock)
        client_event = GameEvent(code=code, message=message, player_number=player_number)
        server_notification_queue.put(client_event)


def get_player_state_message(player_number):
    player_state = players_states[player_number]
    serialized_player_data = pickle.dumps(player_state.player_data)
    return serialized_player_data


def notify_create_player(player_number):
    serialized_player_data = get_player_state_message(player_number)
    notify_player(player_number, serialized_player_data, ProtocolCodes.CREATE_PLAYER)


def notify_player_state(notified_player_number, player_changed_number):
    print(f"player {notified_player_number} is notified on player {player_changed_number} change")
    serialized_player_data = get_player_state_message(player_changed_number)
    notify_player(notified_player_number, serialized_player_data, ProtocolCodes.PLAYER_STATE)


def notify_start_game(player_number):
    notify_player(player_number, b'', ProtocolCodes.START_GAME)
    print(f"sent START_GAME to player {player_number}")


def notify_player(player_number, message, code):
    player_state = players_states[player_number]
    client_socket = player_state.client_socket
    print(f"notify player {player_number} on {code}")
    GameProtocol.send_data(client_socket, code, message)


def create_player_state(client_socket, player_number):
    state = PlayerState(client_socket=client_socket)
    players_states[player_number] = state


def create_player(player_number):
    state = players_states[player_number]
    player_data = create_player_data(player_number)
    state.player_data = player_data
    return player_data


def start_game(server_notification_queue):
    event = GameEvent(code=ProtocolCodes.START_GAME)
    server_notification_queue.put(event)


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
        if player_number == 4:
            time.sleep(2)
            start_game(server_notification_queue)
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