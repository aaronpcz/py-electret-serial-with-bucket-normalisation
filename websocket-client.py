from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from threading import Thread

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
        self.socketio.emit('auth', {'password': 'kittens'}, self.on_auth_r)

        self.receive_events_thread = Thread(target=self._receive_events_thread)
        self.receive_events_thread.daemon = True
        self.receive_events_thread.start()

    def _receive_events_thread(self):
        self.socketio.wait()

    def publish(self):
        self.socketio.emit('sendCommand', 'electret', 'showScenesAndThemes', score)


#
# def on_auth_r(*args):
#     print('on_auth_r', args)
#
#
# def on_connect():
#     print('connect')
#
#
# def on_disconnect():
#     print('disconnect')
#
#
# def on_reconnect():
#     print('reconnect')
#
#
# def on_show_scenes_and_themes(*args):
#     print('on_show_scenes_and_themes', args)
#
#
# socketIO = SocketIO(media_hub_url, 80, LoggingNamespace)
#
# # APEP authenticate with web sockets
# socketIO.emit('auth', {'password': 'kittens'}, on_auth_r)
# socketIO.wait_for_callbacks(seconds=10)
#
# socketIO.on('connect', on_connect)
# socketIO.on('disconnect', on_disconnect)
# socketIO.on('reconnect', on_reconnect)
#
# # socketIO.emit('sendCommand', data=('electret', 'showScenesAndThemes', score))
# socketIO.emit('sendCommand', 'electret', 'showScenesAndThemes', score)
#
# # electret_namespace.emit('sendCommand', payload, on_show_scenes_and_themes)
#
# socketIO.wait()