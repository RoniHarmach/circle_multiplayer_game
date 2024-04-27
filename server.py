import socket, threading, pickle, pygame, time
from queue import Queue
from typing import Dict
from player_data import PlayerData
from game_protocol import GameProtocol
from player_state import PlayerState
from protocol_codes import ProtocolCodes

players_states: Dict[str, PlayerState] = {}

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


def create_player_data():
    player_number = len(players_states) + 1
    player_data = PlayerData(player_initial_coords[player_number - 1], player_colors[player_number - 1], player_number)
    return player_data


def logtcp(dir, tid, byte_data):

    if dir == 'sent':
        print(f'{tid} S LOG:Sent     >>> {byte_data}')
    else:
        print(f'{tid} S LOG:Recieved <<< {byte_data}')



def handle_client(sock, tid, addr):
    global all_to_die
    finish = False
    print(f'New Client number {tid} from {addr}')
    player_data = create_player_data()
    state = PlayerState(client_socket=sock, player_data=player_data)
    players_states[player_data.player_number] = state
    serialized_player = pickle.dumps(player_data)
    GameProtocol.send_data(sock, ProtocolCodes.CREATE_PLAYER, serialized_player)
    time.sleep(2)
    GameProtocol.send_data(sock, ProtocolCodes.START_GAME, b'')

    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        code, message = GameProtocol.read_data(sock)

        print(f"code: {code}")



def accept_clients(srv_sock):
    threads = []
    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()  # accepts an incoming connection request from a TCP client.
        # (clientConnection, clientAddress) = serverSocket.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()  # אומרת לתוכנית לפתוח את הטרד ולהריץ את ההנדל קליינט
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