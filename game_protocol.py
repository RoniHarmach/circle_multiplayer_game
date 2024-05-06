from protocol_codes import ProtocolCodes


class GameProtocol:
    DELIMITER = '#'

    @staticmethod
    def send_data(sock, code, bdata):

        content = code.value.encode() + GameProtocol.DELIMITER.encode() + bdata
        bytearray_data = str(len(content)).zfill(8).encode() \
                         + GameProtocol.DELIMITER.encode() \
                         + content
        index = 0
        while index < len(bytearray_data):
            size = min(1000, len(bytearray_data) - index)
            sock.send(bytearray_data[index:index + size])
            index += size

    @staticmethod
    def split_length_field(byte_data):
        length = int(byte_data[:8].decode())
        byte_data = byte_data[9:]
        return length, byte_data

    def recv_message(sock):
        message = sock.recv(1000)

        if message == b'':
            return message

        message_size = int(message[:8].decode())
        current_size = len(message[9:])
        while (current_size < message_size):
            current_message = sock.recv(1000)
            message += current_message
            current_size += len(current_message)

        return message

    @staticmethod
    def read_data(sock):
        data = sock.recv(1000)
        message_size, message = GameProtocol.split_length_field(data)
        current_size = len(message)
        while current_size < message_size:
            current_message = sock.recv(1000)
            message += current_message
            current_size += len(current_message)

        code_value = message[:4].decode()
        return ProtocolCodes(code_value), message[5:]
