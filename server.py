import socket, threading
from player_data import PlayerData
from game_protocol import GameProtocol
import pickle
from protocol_codes import ProtocolCodes


all_to_die = False  # global

player_colors = [
    (255, 0, 0), #RED
    (0, 255, 0), #GREEN
    (0, 0, 255) #BLUE
 ]

player_coords = [
    (10, 20), (130, 50), (100, 120)
]

players = []


def open_server_socket():
    srv_sock = socket.socket()
    port = 5151
    srv_sock.bind(('0.0.0.0', port))
    srv_sock.listen(2)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return srv_sock


def create_player():
    player_number = len(players) + 1
    player = PlayerData(player_coords[player_number-1], player_colors[player_number-1], player_number)
    return player



def handle_client(sock, tid, addr):
    global all_to_die
    finish = False
    print(f'New Client number {tid} from {addr}')
    player = create_player()
    players.append(player)

    serialized_player = pickle.dumps(player)

    GameProtocol.send_data(sock, ProtocolCodes.CREATE_PLAYER, serialized_player)

    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        try:
            byte_data = sock.recv(1000)  # todo improve it to recv by message size
            if byte_data == b'':
                print('Seems client disconnected')
                break
            logtcp('recv',tid, byte_data) # print
            err_size = check_length(byte_data)
            if err_size != b'':
                to_send = err_size
            else:
                byte_data = byte_data[9:]   # remove length field
                to_send , finish = handle_request(byte_data)
            if to_send != '':
                send_data(sock, tid , to_send) # אפ לא ריק מחזיר את המידע על הבקשה של הלקוח
            if finish:
                time.sleep(1)
                break
        except socket.error as err:
            print(f'Socket Error exit client loop: err:  {err}')
            break
        except Exception as  err:
            print(f'General Error %s exit client loop: {err}')
            print(traceback.format_exc())
            break

    print(f'Client {tid} Exit')
    sock.close()

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