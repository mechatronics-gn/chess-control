import chess
import chess.engine
import serial
from motor import Motor
from controller import Controller
from time import sleep

motor_port = "/dev/ttyACM0"
controller_port = "/dev/ttyACM1"
engine_path = "/usr/bin/stockfish"

motor_serial = serial.Serial(motor_port, 9600)
controller_serial = serial.Serial(controller_port, 9600)

time = 600000
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Skill Level": 5})

motor = Motor(motor_serial)
ctrl = Controller(controller_serial)

while True:
    board = chess.Board()
    ctrl.reset_game(time)
    black_giveup = False
    white_timeout = False
    while not board.is_game_over():
        """
        read white move
        """
        flag = True
        while flag:
            inc = ctrl.read()
            if not inc[0]:
                if inc[1] == "reset":
                    break
                elif inc[1] == "timeout":
                    white_timeout = True
                    break
            else:
                uci = f"{inc[0]}{inc[1]}"
                """
                Support special cases
                """
                if inc[0] == 'e1':
                    if inc[1] == 'h1':  # short side castling
                        if chess.Move.from_uci("e1g1") in board.legal_moves:
                            uci = "e1g1"
                    elif inc[1] == 'a1':
                        if chess.Move.from_uci("e1c1") in board.legal_moves:
                            uci = "e1c1"

                if chess.Move.from_uci(uci+"q") in board.legal_moves:
                    promo_flag = True
                    while promo_flag:
                        print("Promote to: [q/b/n/r]")
                        x = input()
                        if x in ['q', 'b', 'n', 'r']:
                            uci = uci+x
                            promo_flag = False

                move = chess.Move.from_uci(uci)

                if move in board.legal_moves:
                    ctrl.write_coord_ok()
                    ctrl.write_algebraic_expression(board.san(move))
                    if board.is_capture(move):
                        print(f"{board.san(move)} is capturing")
                    board.push(move)
                    motor.move_piece(uci[0:2], uci[2:4])
                    flag = False
                else:
                    ctrl.write_coord_illegal()

        if board.is_game_over():
            break

        """
        black moves
        """
        ctrl.write_cpu_turn()

        black_result = engine.play(board, chess.engine.Limit(time=0.1))
        if black_result.move is not None:
            move = black_result.move
            ctrl.write_algebraic_expression(board.san(move))
            if board.is_castling(move):
                if board.is_kingside_castling(move):
                    motor.move_piece("e8", "g8")
                    motor.move_piece("h8", "f8")
                elif board.is_queenside_castling(move):
                    motor.move_piece("e8", "c8")
                    motor.move_piece("a8", "d8")
            elif move.promotion is not None:
                print(f"{move.to_square} is promoting to {move.promotion}")
                motor.move_piece(chess.square_name(move.from_square), chess.square_name(move.to_square))
            else:
                motor.move_piece(chess.square_name(move.from_square), chess.square_name(move.to_square))
            if board.is_capture(move):
                print(f"{board.san(move)} is capturing")
            board.push(move)
        else:
            black_giveup = True
            break

        if board.is_game_over():
            break

        """
        white moves
        """
        ctrl.write_your_turn()

    if black_giveup:
        ctrl.write_your_win()
        print("White wins (resign)")
    elif white_timeout:
        ctrl.write_cpu_win()
        print("Black wins (timeout")
    else:
        outcome = board.outcome()
        print(f"{outcome.winner} wins")
        if outcome.winner == chess.WHITE:
            ctrl.write_your_win()
        else:
            ctrl.write_cpu_win()

    sleep(5)

