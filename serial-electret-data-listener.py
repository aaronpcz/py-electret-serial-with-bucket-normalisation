import serial
import time
import threading
import socket
from models import osc_command_pb2
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace

media_hub_url = 'http://uos-mediahub.azurewebsites.net'

# serial connection
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud)

osc_string_target = "/eos/chan/20"

score_blank = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "595f5da2d2e6e9ac8a6d8c44"
            ]
        }
    }

score_1 = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "595f4752d2e6e9ac8a6d8c3b"
            ]
        }
    }

score_2 = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "595f4752d2e6e9ac8a6d8c3b"
            ]
        }
    }

score_3 = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "595f47b5d2e6e9ac8a6d8c3d"
            ]
        }
    }

score_4 = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "595f47cad2e6e9ac8a6d8c3e"
            ]
        }
    }


class PublishMediaFrameworkMessages:

    def on_auth_r(self, *args):
        print('on_auth_r', args)

    def __init__(self):
        self.socketio = SocketIO(media_hub_url, 80, LoggingNamespace)
        self.socketio.emit('auth', {'password': 'kittens'}, self.on_auth_r)

        self.receive_events_thread = threading.Thread(target=self._receive_events_thread)
        self.receive_events_thread.daemon = True
        self.receive_events_thread.start()

    def _receive_events_thread(self):
        self.socketio.wait()

    def publish(self, room, s):
        print('publish')
        self.socketio.emit('sendCommand', room, 'showScenesAndThemes', s)


class State:

    def __init__(self, state_name, state_manager):
        self.name = state_name
        self.state_manager = state_manager

    def state_transition(self):
        print("State state transition")

    def receive_data(self, data):
        print("State - receive_data - data: " + data)

    def run_state(self):
        print("State - run state")


class DirectAcousticLightControlState(State):

    def __init__(self, state_name, state_manager, num):
        State.__init__(self, state_name, state_manager)
        self.activation_number = num
        self.state_num = 1

    def get_score_from_state_num(self):
        score = None
        if self.state_num == 1:
            score = score_1
        elif self.state_num == 2:
            score = score_2
        elif self.state_num == 3:
            score = score_3
        elif self.state_num == 4:
            score = score_4
        self.state_num = self.state_num + 1
        if self.state_num > 4:
            self.state_num = 1

        return score

    def state_transition(self):
        print("DirectAcousticLightControlState state transition")

    def run_state(self):
        print("DirectAcousticLightControlState - Publish UDP or WS")

        self.state_manager.ws_messenger.publish("mirroringlife", self.get_score_from_state_num())
        udp_client.send_string_data(osc_string_target, "max")

    def receive_data(self, data):
        print("DirectAcousticLightControlState - receive_data - data: " + str(data))

        udp_client.send_numerical_data(osc_string_target, data)

        if data > self.activation_number:
            self.run_state()
            self.state_manager.to_second_state()


class FullLightsOnAndWaitState(State):

    def __init__(self, state_name, state_manager, num):
        State.__init__(self, state_name, state_manager)
        self.activation_number = num
        self.timestamp = time.time()
        self.transition_to_next_state_time = self.timestamp + 10

    def state_transition(self):
        print("FullLightsOnAndWaitState - state_transitioned")
        self.timestamp = time.time()
        self.transition_to_next_state_time = self.timestamp + 10

    def run_state(self):
        print("FullLightsOnAndWaitState - Publish UDP or WS")

        self.state_manager.ws_messenger.publish("mirroringlife", score_blank)

    def receive_data(self, data):
        print("FullLightsOnAndWaitState - receive_data - data: " + str(data))
        # print(time.time())
        # print(self.transition_to_next_state_time)
        if time.time() > self.transition_to_next_state_time:
            self.run_state()
            self.state_manager.to_first_state()


class StateMachineManager:

    def __init__(self, udp):
        self.first_state = DirectAcousticLightControlState("one", self, 95)
        self.second_state = FullLightsOnAndWaitState("two", self, 40)
        self.udp = udp

        self.current_state = self.first_state
        self.ws_messenger = PublishMediaFrameworkMessages()

    def to_first_state(self):
        self.current_state = self.first_state
        self.current_state.state_transition()

    def to_second_state(self):
        self.current_state = self.second_state
        self.current_state.state_transition()


class UDPClient:

    def __init__(self):
        # self.HOST, self.PORT = "127.0.0.1", 9999
        # self.HOST, self.PORT = "192.168.0.42", 9999
        self.HOST, self.PORT = "10.99.168.53", 9999

        # APEP SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_osc_command(self, command):
        self.sock.sendto(command.SerializeToString(), (self.HOST, self.PORT))
        print(time.time())
        # print("Sent:     {} {}".format(command, len(command.SerializeToString())))

    def send_numerical_data(self, target, int_value):
        command = osc_command_pb2.OSCCommand()
        command.target = target
        command.type = 0
        command.value = int_value
        command.time_stamp = time.time()
        self.send_osc_command(command)

    def send_string_data(self, target, s_value):
        command = osc_command_pb2.OSCCommand()
        command.target = target
        command.type = 1
        command.s_value = s_value
        command.time_stamp = time.time()
        self.send_osc_command(command)


udp_client = UDPClient()
state = StateMachineManager(udp_client)

min_allowed = 1
max_allowed = 100

mic_range_min = 0
mic_range_max = 1000


def rescale(i_value):
    return int(((i_value - mic_range_min) / (mic_range_max - mic_range_min)) * (max_allowed - min_allowed) + min_allowed)


def handle_data_for_continuous_control(data):
    try:
        electret_peak_sample = int(data)
        print(electret_peak_sample)
        rescaled_peak_sample = rescale(electret_peak_sample)
        state.current_state.receive_data(rescaled_peak_sample)
    except Exception as e:
        print("Error: " + str(e))


def handle_data_for_discrete_output(data):
    try:
        print(data)
        electret_peak_sample = int(data)
        if electret_peak_sample < 50:
            print("very quiet")
            udp_client.send_numerical_data(osc_string_target, 15)
        elif electret_peak_sample < 500:
            print("medium noise")
            udp_client.send_numerical_data(osc_string_target, 50)
        else:
            print("noisy")
            udp_client.send_numerical_data(osc_string_target, 100)
    except Exception as e:
        print("Error: " + str(e))


def read_from_port(ser):
    # read serial port for data
    while True:
        reading = ser.readline()
        electret_peak_sample = reading
        handle_data_for_continuous_control(electret_peak_sample)


if __name__ == "__main__":
    thread = threading.Thread(target=read_from_port, args=(serial_port,))
    thread.start()