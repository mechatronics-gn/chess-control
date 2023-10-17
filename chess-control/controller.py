import serial


class Controller:
    def __init__(self, ctrl_serial: serial.Serial):
        self.serial = ctrl_serial

    def reset_game(self, time: int):
        self.serial.write(bytes(bytearray([0, (time >> 24) % 256, (time >> 16) % 256, (time >> 8) % 256, time % 256])))

    def write_coord_ok(self):
        self.serial.write(b'\x01')

    def write_coord_illegal(self):
        self.serial.write(b'\x02')

    def write_algebraic_expression(self, exp: str):
        exp = exp[:8]
        self.serial.write(bytes(bytearray([3, len(exp)])))
        self.serial.write(bytes(exp, 'ascii'))

    def write_your_turn(self):
        self.serial.write(b'\x04')

    def write_cpu_turn(self):
        self.serial.write(b'\x05')

    def write_your_win(self):
        self.serial.write(b'\x06')

    def write_cpu_win(self):
        self.serial.write(b'\x07')

    def read(self) -> (str, str):
        ty = self.serial.read(size=1)
        if int(ty[0]) == int(b'\xAB'):
            return "", "reset"
        elif int(ty[0]) == int(b'\xAC'):
            data = self.serial.read(size=4)

            ret1 = ""
            ret1 += chr(int(data[0]) + 97)
            ret1 += chr(int(data[1]) + 49)

            ret2 = ""
            ret2 += chr(int(data[2]) + 97)
            ret2 += chr(int(data[3]) + 49)

            return ret1, ret2
        elif int(ty[0]) == int(b'\xAD'):
            return "", "timeout"



