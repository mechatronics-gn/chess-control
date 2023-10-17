import chess
import chess.engine
import serial
from reed import read_reed, comp_reed
from motor import Motor

motor_port = "/dev/ttyACM0"

motor_serial = serial.Serial(motor_port, 9600)

motor = Motor(motor_serial)
print("Motor init done")

while True:
    motor.query_stepper(1170, 1200)
    motor.query_servo(False)
    motor.query_reset()
    motor.query_servo(True)
