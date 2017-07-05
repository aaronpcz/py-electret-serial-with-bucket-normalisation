import serial
import time
import threading
import socket
from models import osc_command_pb2
# serial connection
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud)

osc_string_target = "/eos/chan/17"


class UDPClient:

    def __init__(self):
        # self.HOST, self.PORT = "127.0.0.1", 9999
        # self.HOST, self.PORT = "192.168.0.42", 9999
        self.HOST, self.PORT = "10.100.164.29", 9999

        # APEP SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_osc_command(self, command):
        self.sock.sendto(command.SerializeToString(), (self.HOST, self.PORT))
        print(time.time())
        print("Sent:     {} {}".format(command, len(command.SerializeToString())))

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

min_allowed = 0
max_allowed = 100

mic_range_min = 40
mic_range_max = 1000


def rescale(i_value):
    return ((max_allowed - min_allowed) * (i_value * mic_range_min) / (mic_range_max - mic_range_min)) + min_allowed;


def handle_data_for_continuous_control(data):
    try:
        electret_peak_sample = int(data)
        rescaleed_peak_sample = rescale(electret_peak_sample)
        udp_client.send_numerical_data(osc_string_target, rescaleed_peak_sample)
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