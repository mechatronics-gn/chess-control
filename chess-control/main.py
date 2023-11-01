import chess
import chess.engine
import random
import serial
from motor import Motor
from controller import Controller
from time import sleep

motor_port = "/dev/ttyACM0"
controller_port = "/dev/ttyUSB0"
engine_path = "/usr/bin/stockfish"

motor_serial = serial.Serial(motor_port, 9600)
controller_serial = serial.Serial(controller_port, 9600)

time = 600000
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
engine.configure({"Threads": 1})
engine.configure({"Skill Level": 0})

motor = Motor(motor_serial)
ctrl = Controller(controller_serial)

while True:
    board = chess.Board()
    black_giveup = False
    white_timeout = False
    difficulty_flag = True
    is_easy = False
    while difficulty_flag:
        print("Difficulty: easy/hard [e/h]")
        x = input()
        if x == 'e':
            is_easy = True
            difficulty_flag = False
        elif x == 'h':
            is_easy = False
            difficulty_flag = False

    motor.query_reset()

    for i in ['8', '7', '2', '1']:
        list_a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        list_b = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
        if i == '8' or i == '2':
            l = list_a
        else:
            l = list_b
        for j in l:
            motor.query_servo(False)
            motor.goto_square(j+i)
            motor.query_servo(True)
            sleep(1)

    ctrl.reset_game(time)

    while not board.is_game_over():
        """
        read white move
        """
        flag = True
        while flag:
            inc = ctrl.read()
            if not inc[0]:
                if inc[1] == "reset":
                    ctrl.reset_game(time)
                    continue
                elif inc[1] == "timeout":
                    white_timeout = True
                    break
                elif inc[1] == "debug":
                    continue
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

                try:
                    if chess.Move.from_uci(uci + "q") in board.legal_moves:
                        promo_flag = True
                        while promo_flag:
                            print("Promote to queen/bishop/knight/rook : [q/b/n/r]")
                            x = input()
                            if x in ['q', 'b', 'n', 'r']:
                                uci = uci + x
                                promo_flag = False
                except chess.InvalidMoveError:
                    pass

                try:
                    move = chess.Move.from_uci(uci)

                    if move in board.legal_moves:
                        ctrl.write_coord_ok()
                        ctrl.write_algebraic_expression(board.san(move))
                        if board.is_castling(move):
                            if board.is_kingside_castling(move):
                                motor.move_piece("e1", "g1")
                                motor.move_piece("h1", "f1")
                            elif board.is_queenside_castling(move):
                                motor.move_piece("e1", "c1")
                                motor.move_piece("a1", "d1")
                        else:
                            motor.move_piece(uci[0:2], uci[2:4])
                        if board.is_capture(move):
                            print(f"Capturing: {board.san(move)} is capturing")
                        board.push(move)
                        flag = False
                    else:
                        ctrl.write_coord_illegal()
                except chess.InvalidMoveError:
                    ctrl.write_coord_illegal()

        if board.is_game_over() or white_timeout:
            break

        """
        black moves
        """
        ctrl.write_cpu_turn()

        move = None
        while move is None:
            if is_easy:
                idx = random.randint(0, board.legal_moves.count()-1)
                i = 0
                for move in board.legal_moves:
                    i += 1
                    if i > idx:
                        break
            else:
                result = engine.play(board, chess.engine.Limit(time=0.000000001, depth=0))
                if result.move is None:
                    black_giveup = True
                    break
                move = result.move
            if board.is_en_passant(move):
                move = None
            if move.promotion is not None:
                if move.promotion != chess.QUEEN:
                    move = None
        if black_giveup:
            break

        ctrl.write_algebraic_expression(board.san(move))
        if board.is_castling(move):
            if board.is_kingside_castling(move):
                 motor.move_piece("e8", "g8")
                 motor.move_piece("h8", "f8")
            elif board.is_queenside_castling(move):
                motor.move_piece("e8", "c8")
                motor.move_piece("a8", "d8")
        elif move.promotion is not None:
            print(f"CPU Promoting: {move.to_square} is promoting to {move.promotion}")
            motor.move_piece(chess.square_name(move.from_square), chess.square_name(move.to_square))
        else:
            motor.move_piece(chess.square_name(move.from_square), chess.square_name(move.to_square))
        if board.is_capture(move):
            print(f"Capturing: {board.san(move)} is capturing")
        board.push(move)

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
        elif outcome.winner == chess.BLACK:
            ctrl.write_cpu_win()
        else:
            ctrl.write_draw()

    sleep(5)
