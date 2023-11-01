import serial
import time


class Controller:
    def __init__(self, ctrl_serial: serial.Serial):
        self.serial = ctrl_serial

    def reset_game(self, time: int):
        print("Writing reset with " + str(bytes(bytearray([0, (time >> 24) % 256, (time >> 16) % 256, (time >> 8) % 256, time % 256]))))
        self.serial.write(bytes(bytearray([0, (time >> 24) % 256, (time >> 16) % 256, (time >> 8) % 256, time % 256])))

    def write_coord_ok(self):
        self.serial.write(b'\x01')

    def write_coord_illegal(self):
        self.serial.write(b'\x02')

    def write_algebraic_expression(self, exp: str):
        exp = exp[:8]
        self.serial.write(bytes(bytearray([3, len(exp)])))
        self.serial.write(bytes(exp, 'ascii'))
        print(f"Sent {exp} to ctrl")

    def write_your_turn(self):
        self.serial.write(b'\x04')

    def write_cpu_turn(self):
        self.serial.write(b'\x05')

    def write_your_win(self):
        self.serial.write(b'\x06')

    def write_cpu_win(self):
        self.serial.write(b'\x07')

    def write_draw(self):
        self.serial.write(b'\x08')

    def read(self) -> (str, str):
        ty = self.serial.read(size=1)
        if int(ty[0]) == int(b'\xAB'[0]):
            return "", "reset"
        elif int(ty[0]) == int(b'\xAC'[0]):
            data = self.serial.read(size=4)

            ret1 = ""
            ret1 += chr(int(data[0]) + 97)
            ret1 += chr(int(data[1]) + 49)

            ret2 = ""
            ret2 += chr(int(data[2]) + 97)
            ret2 += chr(int(data[3]) + 49)

            return ret1, ret2
        elif int(ty[0]) == int(b'\xAD'[0]):
            return "", "timeout"
        elif int(ty[0]) == int(b'\xAE'[0]):
            print("debug: " + str(self.serial.read_until(), 'ascii'), end="")
            return "", "debug"



