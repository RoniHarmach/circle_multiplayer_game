from protocol_codes import ProtocolCodes

DELIMITER = '#'
DELIMITER_LEN = 1
CONTENT_SIZE_LEN = 8
CODE_LEN = 4
READ_BATCH_SIZE = 1000


class GameProtocolError(Exception):
    pass


class GameProtocol:

    @staticmethod
    def send_data(sock, code, bdata):
        content = code.value.encode() + DELIMITER.encode() + bdata
        bytearray_data = str(len(content)).zfill(CONTENT_SIZE_LEN).encode() \
                         + DELIMITER.encode() \
                         + content

        index = 0
        while index < len(bytearray_data):
            size = min(READ_BATCH_SIZE, len(bytearray_data) - index)
            sock.send(bytearray_data[index:index + size])
            index += size

    @staticmethod
    def split_length_field(byte_data):
        length = int(byte_data[:CONTENT_SIZE_LEN].decode())
        byte_data = byte_data[(CONTENT_SIZE_LEN + DELIMITER_LEN):]
        return length, byte_data


    @staticmethod
    def read_data(sock):
        try:
            data = sock.recv(READ_BATCH_SIZE)
            if data == b'':
                return ProtocolCodes.CLIENT_DISCONNECTED, b''
            if len(data) < CONTENT_SIZE_LEN + DELIMITER_LEN + CODE_LEN:
                raise GameProtocolError(f"Message is invalid. Length is {len(data)}")

            message_size, message = GameProtocol.split_length_field(data)
            current_size = len(message)
            while current_size < message_size:
                current_message = sock.recv(READ_BATCH_SIZE)
                message += current_message
                current_size += len(current_message)

            code_value = message[:CODE_LEN].decode()
            return ProtocolCodes(code_value), message[(CODE_LEN + DELIMITER_LEN):]
        except ConnectionResetError:
            return ProtocolCodes.CLIENT_DISCONNECTED, b''

