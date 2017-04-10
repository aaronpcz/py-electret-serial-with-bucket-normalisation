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

green_scene = "58eb7eba2261fd6c10a8c65a"
yellow_scene = "58eb7ec62261fd6c10a8c65b"
red_scene = "58eb7ece2261fd6c10a8c65c"


def get_score_for_scene(scene_id):
    return {
        "play": {
            "themes": [
            ],
            "scenes": [
                scene_id
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

        self.published_score = get_score_for_scene("")

        while True:
            reading = serial_port.readline()
            electret_peak_sample = reading
            score_to_play = handle_data(electret_peak_sample)
            if not self.published_score == score_to_play:
                self.publish(score_to_play)
                self.published_score = score_to_play

    def _receive_events_thread(self):
        self.socketio.wait()

    def publish(self, score_to_play):
        self.socketio.emit('sendCommand', 'electret', 'showScenesAndThemes', score_to_play)


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
            return get_score_for_scene(green_scene)
        elif electret_peak_sample < 500:
            print("medium noise")
            return get_score_for_scene(yellow_scene)
        else:
            print("noisy")
            return get_score_for_scene(red_scene)
    except:
        print("Error")
        return get_score_for_scene("")


def main():
    ws_messenger = PublishMediaFrameworkMessages()

if __name__ == "__main__":
    main()
