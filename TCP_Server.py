import socket
import configparser


class TCP_Server:
    def __init__(self):
        self.config = configparser.ConfigParser()  # создаём объекта парсера
        self.config.read("settings.ini")  # читаем конфиг

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.host = str(s.getsockname()[0])
        s.close()

        self.port = int(self.config["Server"]["port"])  # получаем значение параметра port
        self.SERVER_ADDRESS = (self.host, self.port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.SERVER_ADDRESS)
        self.connection = None
        self.address = None
        self.data = None

    def get_state(self): # Get current state of boiler
        self.server_socket.listen()
        self.connection, self.address = self.server_socket.accept()
        while True:
            self.send_data(bytes.fromhex("AA03081004C9"))  # Request state. AA03081004C9 hex command to get state
            data = self.connection.recv(4096)
            if len(data) == 13:
                self.connection.close()
                self.connection = None
                return data

    def set_parameters(self, data): # Set parameters of boiler
        self.server_socket.listen()
        self.connection, self.address = self.server_socket.accept()
        self.send_data(data)
        self.connection.close()
        self.connection = None

    def send_data(self, data): # Send data in hex format to boiler
        self.connection.sendto(data, (self.config["Client"]["address"], int(self.config["Client"]["port"])))
        from time import sleep
        sleep(0.2)
        self.connection.sendto(data, (self.config["Client"]["address"], int(self.config["Client"]["port"])))
        sleep(0.2)
        self.connection.sendto(data, (self.config["Client"]["address"], int(self.config["Client"]["port"])))


if __name__ == '__main__':
    tcp_server = TCP_Server()
    # tcp_server.get_state()
    tcp_server.set_parameters(bytes.fromhex("AA040A000132eb"))
    print("HERE?")
