from enum import Enum
import TCP_Server


class Boiler:
    def __init__(self):
        self.state = BoilerState.OFF
        self.temperature = -1
        self.targetTemperature = -1
        self.timer_days = 0
        self.timer_hours = 0
        self.antibacterial = 0
        self.tcp_server = TCP_Server.TCP_Server()
        self.get_state()

    def get_state(self):
        data = self.tcp_server.get_state()
        if(data[3] == 0):
            self.state = BoilerState.OFF
        elif(data[3] == 1):
            self.state = BoilerState.POWER_1
        elif(data[3] == 2):
            self.state = BoilerState.POWER_2
        elif(data[3] == 3):
            self.state = BoilerState.POWER_3
        elif(data[3] == 4):
            self.state = BoilerState.POWER_TIMER
        elif(data[3] == 5):
            self.state = BoilerState.POWER_NOFROST
        else:
            self.state = BoilerState.UNKNOWN
        self.temperature = data[4]
        self.targetTemperature = data[5]
        if self.state == BoilerState.POWER_TIMER:
            self.timer_days = data[8]
            self.timer_hours = data[9]
        self.antibacterial = data[11]
        return 0

    def set_state(self):
        if self.state != BoilerState.UNKNOWN:
            if 75 >= self.targetTemperature >= 0:
                hex_string = r"AA040A000" + hex(self.state.value)[2:] + hex(self.targetTemperature)[2:]
                checksum = (184 + self.state.value + self.targetTemperature) % 256  # Calculate checksum
                if checksum < 10:
                    hex_string += "0" + hex(checksum)[2:]
                else:
                    hex_string += hex(checksum)[2:]
                print(hex_string)
                self.tcp_server.set_parameters(bytes.fromhex(hex_string))
                if self.antibacterial == 0:
                    hex_string = r"AA030A0300BA"
                else:
                    hex_string = r"AA030A0301BB"
                self.tcp_server.set_parameters(bytes.fromhex(hex_string))
                return 0
            else:
                return 1
        else:
            return 2




class BoilerState(Enum):
    OFF = 0
    POWER_1 = 1
    POWER_2 = 2
    POWER_3 = 3
    POWER_TIMER = 4
    POWER_NOFROST = 5
    UNKNOWN = 6

if __name__ == '__main__':
    print(BoilerState(1) == BoilerState.POWER_1)
    # my_boiler = Boiler()
    # my_boiler.get_state()
    # my_boiler.targetTemperature = 35
    # my_boiler.state = BoilerState.POWER_3
    # my_boiler.antibacterial = 0
    # my_boiler.set_state()
