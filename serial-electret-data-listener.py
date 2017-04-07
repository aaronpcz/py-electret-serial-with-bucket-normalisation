import serial
import time
import threading
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from threading import Thread
from tendo import singleton
import configparser
import sys

me = singleton.SingleInstance()

config = configparser.ConfigParser()
config.read('./config.cfg')

password = config.get('variables', 'password')

media_hub_url = 'http://dev-uos-mediahub.azurewebsites.net'

score = {
        "play": {
            "themes": [
            ],
            "scenes": [
                "586f853ab8678acc10b1595d"
            ]
        }
    }


class PublishMediaFrameworkMessages:
    def on_auth_r(self, *args):
        print('on_auth_r', args)

    def __init__(self):
        self.socketio = SocketIO(media_hub_url, 80, LoggingNamespace)
        self.socketio.emit('auth', {'password': password}, self.on_auth_r)
        self.socketio.wait_for_callbacks(seconds=10)

        self.receive_events_thread = Thread(target=self._receive_events_thread)
        self.receive_events_thread.daemon = True
        self.receive_events_thread.start()

        yes = False

        while True:
            reading = serial_port.readline()
            electret_peak_sample = reading
            handle_data(electret_peak_sample)
            self.publish(yes)
            yes = True

    def _receive_events_thread(self):
        self.socketio.wait()

    def publish(self, should_publish):
        print("publish")
        print(should_publish)
        if not should_publish:
            self.socketio.emit('sendCommand', 'electret', 'showScenesAndThemes', score)
        if should_publish:
            sys.exit('we have published')


# serial connection
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud)


def handle_data(data):
    try:
        print(data)
        electret_peak_sample = int(data)
        if electret_peak_sample < 50:
            print("very quiet")
        elif electret_peak_sample < 500:
            print("medium noise")
        else:
            print("noisy")
    except:
        print("Error")


def main():
    ws_messenger = PublishMediaFrameworkMessages()

if __name__ == "__main__":
    main()
