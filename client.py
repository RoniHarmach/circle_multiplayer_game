import socket, sys, pickle, pygame, threading
from game_protocol import GameProtocol
from protocol_codes import ProtocolCodes
from player import Player

WIDTH, HEIGHT = 800, 600
pygame.init()
server_socket = None
player = None


def open_client_socket(ip):
    connected = False
    sock = socket.socket()
    port = 6060
    try:
        sock.connect((ip, port))
        print(f'Connect succeeded {ip}:{port}')
        connected = True
        return sock, connected
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
    return sock, connected


def handle_client_event(player):
    running = True
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    background_image_path = "sprire/entry_background.jpeg"
    background_image = pygame.image.load(background_image_path).convert()
    screen.blit(background_image, (0, 0))
    pygame.display.flip()


"""    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(pygame.Color("white"))
        player.update(mouse_pos)
        player.draw(screen)
        pygame.display.update()
        pygame.time.Clock().tick(40)  # Limit to 60 frames per second

    pygame.quit()
"""


def handle_create_player(bdata):
    deserialized_player = pickle.loads(bdata)
    player = Player(deserialized_player)
    load_entry_screen()


def load_entry_screen():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    background_image_path = "sprite/entry_background.jpeg"
    background_image = pygame.image.load(background_image_path).convert()
    screen.blit(background_image, (0, 0))
    pygame.display.flip()

      # running = True
      #   screen = pygame.display.set_mode((WIDTH, HEIGHT))
      #   while running:
      #       for event in pygame.event.get():
      #           if event.type == pygame.QUIT:
      #               running = False
      #       screen.fill(pygame.Color("white"))
      #       player.draw(screen)
      #       pygame.display.update()
      #   pygame.quit()


def handle_message(code, bdata):
    if code == ProtocolCodes.CREATE_PLAYER:
        print("handling create player")
        handle_create_player(bdata)
        load_entry_screen()


def handle_server_messages():
    while True:
        code, byte_data = GameProtocol.read_data(server_socket)
        handle_message(code, byte_data)
        if byte_data == b'':
            print('Seems server disconnected abnormal')
            break


def main(ip):
    global server_socket
    sock, connected = open_client_socket(ip)
    server_socket = sock
    pygame.init()
    events_thread = threading.Thread(target=handle_server_messages)
    events_thread.start()
    events_thread.join()
    # while connected:
    #     code, byte_data = GameProtocol.read_data(server_socket)
    #     handle_message(code, byte_data)
    #     if byte_data == b'':
    #         print('Seems server disconnected abnormal')
    #         break
    #
    #     print("d")
    print('Bye')
    # sock.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')
