import serial


class Motor:
    x_margin = 100
    y_margin = 100
    x_size = 300
    y_size = 300

    def __init__(self, motor_serial: serial.Serial):
        self.state = False
        self.serial = motor_serial
        self.is_servo_up = False
        self.x = 0
        self.y = 0

        self.serial.write(bytearray([3]))

    def query_stepper(self, x: int, y: int):
        while not self.check_state():
            pass
        self.serial.write(bytearray([1, x, y]))
        self.x = x
        self.y = y

    def query_servo(self, is_servo_up: bool):
        while not self.check_state():
            pass
        self.serial.write(bytearray([2, is_servo_up]))
        self.is_servo_up = is_servo_up

    def calculate_square_pos(self, square: str) -> (int, int):
        x = ord(square[0]) - ord('a')
        y = ord(square[1]) - ord('0')
        return self.x_margin + x * self.x_size + self.x_size / 2, self.y_margin + y * self.y_size + self.y_size / 2

    def goto_square(self, square: str):
        (x, y) = self.calculate_square_pos(square)
        self.query_stepper(x, y)

    def goto_line(self, line: str):
        line = line[0]
        if ord('a') <= ord(line) <= ord('i'):
            self.query_stepper(self.x_margin + self.x_size * (ord(line) - ord('a')), self.y)
        if ord('1') <= ord(line) <= ord('9'):
            self.query_stepper(self.x, self.y_margin + self.y_size * (ord(line) - ord('0')))

    def move_piece(self, from_square: str, to_square: str):
        self.query_servo(False)
        self.goto_square(from_square)
        self.query_servo(True)
        self.goto_line(from_square[0])
        self.goto_line(from_square[1])
        self.goto_line(to_square[0])
        self.goto_line(to_square[1])
        self.goto_square(to_square)
        self.query_servo(False)

    def check_state(self):
        if self.serial.in_waiting > 0:
            if self.serial.read() == 1:
                self.state = True
                return True
        self.state = False
        return False

