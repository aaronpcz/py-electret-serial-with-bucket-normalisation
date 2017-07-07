import time
import random
import threading
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace

media_hub_url = 'http://uos-mediahub.azurewebsites.net'

score = {
        "play": {
            "themes": [
                "aaron"
            ],
            "scenes": [
                "aaron 1"
            ]
        }
    }

score_2 = {
        "play": {
            "themes": [
                "aaron 2"
            ],
            "scenes": [
                "aaron 2"
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

    def state_transition(self):
        print("DirectAcousticLightControlState state transition")

    def run_state(self):
        print("DirectAcousticLightControlState - Publish UDP or WS")

        # APEP TODO publish WS message - actual content
        self.state_manager.ws_messenger.publish("DirectAcousticLightControlState", score)

    def receive_data(self, data):
        print("DirectAcousticLightControlState - receive_data - data: " + str(data))

        # APEP TODO publish audio data

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

        # APEP TODO publish WS message - blank message
        self.state_manager.ws_messenger.publish("FullLightsOnAndWaitState", score_2)

    def receive_data(self, data):
        print("FullLightsOnAndWaitState - receive_data - data: " + str(data))

        print(time.time())
        print(self.transition_to_next_state_time)
        if time.time() > self.transition_to_next_state_time:
            self.run_state()
            self.state_manager.to_first_state()


class StateMachineManager:

    def __init__(self):
        self.first_state = DirectAcousticLightControlState("one", self, 95)
        self.second_state = FullLightsOnAndWaitState("two", self, 40)

        self.current_state = self.first_state
        self.ws_messenger = PublishMediaFrameworkMessages()

    def to_first_state(self):
        self.current_state = self.first_state
        self.current_state.state_transition()

    def to_second_state(self):
        self.current_state = self.second_state
        self.current_state.state_transition()


state = StateMachineManager()


def run():
    while True:
        state.current_state.receive_data(random.randint(0, 100))
        time.sleep(0.1)

if __name__ == "__main__":
    thread = threading.Thread(target=run)
    thread.start()

