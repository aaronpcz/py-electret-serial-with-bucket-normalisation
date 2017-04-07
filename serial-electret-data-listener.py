import serial
import time
import threading

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


def read_from_port(ser):
    # read serial port for data
    while True:
        reading = ser.readline()
        electret_peak_sample = reading
        handle_data(electret_peak_sample)


thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()