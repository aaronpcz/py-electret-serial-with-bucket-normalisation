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

osc_value_quiet = 33
osc_value_med = 66
osc_value_loud = 100

osc_chan_401 = "/eos/chan/401"
osc_chan_402 = "/eos/chan/402"
osc_chan_403 = "/eos/chan/403"

osc_chan_default = "/eos/chan/402"

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


def get_osc_command(target, value):
    return {
        "target": target,
        "value": value
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

        self.published_data = handle_data_for_osc("0", osc_chan_default)

        while True:
            reading = serial_port.readline()
            electret_peak_sample = reading
            publish_data = handle_data_for_osc(electret_peak_sample, osc_chan_default)
            if not self.published_data == publish_data:
                self.publish_osc(handle_data_for_osc(electret_peak_sample, osc_chan_401))
                self.publish_osc(handle_data_for_osc(electret_peak_sample, osc_chan_402))
                self.publish_osc(handle_data_for_osc(electret_peak_sample, osc_chan_403))
                self.published_data = publish_data

    def _receive_events_thread(self):
        self.socketio.wait()

    def publish(self, score_to_play):
        if score_to_play:
            print("publish score")
            self.socketio.emit('sendCommand', 'electret', 'showScenesAndThemes', score_to_play)

    def publish_osc(self, osc):
        if osc:
            print("publish oscCommand")
            self.socketio.emit('sendCommand', 'lighting', 'oscCommand', osc)


# serial connection
port = '/dev/ttyACM0'
baud = 9600
serial_port = serial.Serial(port, baud)


def handle_data_for_osc(data, channel):
    try:
        print(data)
        electret_peak_sample = int(data)
        if electret_peak_sample < 100:
            print("very quiet")
            return
        elif electret_peak_sample < 200:
            print("quiet")
            return get_osc_command(channel, osc_value_quiet)
        elif electret_peak_sample < 500:
            print("medium noise")
            return get_osc_command(channel, osc_value_med)
        else:
            print("noisy")
            return get_osc_command(channel, osc_value_loud)
    except:
        print("Error")
        return


# def handle_data_for_osc(data):
#     try:
#         print(data)
#         electret_peak_sample = int(data)
#         if electret_peak_sample < 100:
#             print("very quiet")
#             return
#         elif electret_peak_sample < 200:
#             print("quiet")
#             return get_osc_command(osc_chan_default, osc_value_quiet)
#         elif electret_peak_sample < 500:
#             print("medium noise")
#             return get_osc_command(osc_chan_default, osc_value_med)
#         else:
#             print("noisy")
#             return get_osc_command(osc_chan_default, osc_value_loud)
#     except:
#         print("Error")
#         return


def handle_data(data):
    try:
        print(data)
        electret_peak_sample = int(data)
        if electret_peak_sample < 100:
            print("very quiet")
            return
        elif electret_peak_sample < 200:
            print("quiet")
            return get_score_for_scene(green_scene)
        elif electret_peak_sample < 500:
            print("medium noise")
            return get_score_for_scene(yellow_scene)
        else:
            print("noisy")
            return get_score_for_scene(red_scene)
    except:
        print("Error")
        return


def main():
    ws_messenger = PublishMediaFrameworkMessages()

if __name__ == "__main__":
    main()
