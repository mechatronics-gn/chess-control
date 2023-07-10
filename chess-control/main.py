import chess
import chess.engine
import serial
from reed import read_reed, comp_reed
from motor import Motor

reed_ports = [
    "/dev/ttyACM0",  # a1 코너
    "/dev/ttyACM1",  # h1 코너
    "/dev/ttyACM2",  # a8 코너
    "/dev/ttyACM3",  # h8 코너
    "/dev/ttyACM4",  # 중앙
]
timer_port = "/dev/ttyACM5"
motor_port = "/dev/ttyACM6"
engine_path = "/usr/bin/stockfish"

reed_serials = [serial.Serial(x, 9600) for x in reed_ports]
timer_serial = serial.Serial(timer_port, 9600)
motor_serial = serial.Serial(motor_port, 9600)

reed_before = read_reed(reed_serials)
time = 600
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Skill Level": 5})

motor = Motor(motor_serial)

timeout = False
while not board.is_game_over():
    """
        white moves
    """
    timer_serial.write(1)
    flag = True
    while flag:
        x = timer_serial.read(1)
        if x[0] < 0:  # white lose / timeout
            timeout = True
            break

        reed = read_reed(reed_serials)
        diff = comp_reed(reed_before, reed)

        if diff is not None:  # Move is possible to be valid
            if chess.Move.from_uci(diff) in board.legal_moves:
                board.push_uci(diff)
                print(board)
                flag = False
                time = x[0]
            elif chess.Move.from_uci(diff+"q") in board.legal_moves:  # promotion
                promo_flag = True
                while promo_flag:
                    print("Promotion to: [q/b/n/r]")
                    x = input()
                    if x in ['q', 'b', 'n', 'r']:
                        board.push_uci(diff+x)
                        print(board)
                        flag = False
                        promo_flag = False
                        time = x[0]

        if flag:
            timer_serial.write(0)

    if board.is_game_over():
        break

    """
        black moves
    """

    black_result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(black_result.move)
    motor.move_piece(chess.square_name(black_result.move.from_square), chess.square_name(black_result.move.to_square))
    print(board)

print("Game over")
if timeout:
    print("Black wins (timeout)")
else:
    outcome = chess.Board.outcome()
    print(f"{outcome.winner} wins")
engine.quit()















