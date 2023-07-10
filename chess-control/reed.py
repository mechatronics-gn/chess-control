from serial import Serial

position_map = [
    [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3)],
    [(4, 0), (5, 0), (6, 0), (7, 0), (4, 1), (5, 1), (6, 1), (7, 1), (4, 2), (5, 2), (6, 2), (7, 2), (7, 3)],
    [(0, 4), (0, 5), (1, 5), (2, 5), (3, 5), (0, 6), (1, 6), (2, 6), (3, 6), (0, 7), (1, 7), (2, 7), (3, 7)],
    [(7, 4), (4, 5), (5, 5), (6, 5), (7, 5), (4, 6), (5, 6), (6, 6), (7, 6), (4, 7), (5, 7), (6, 7), (7, 7)],
    [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (-1, -1)],
]


def read_reed(reeds: list[Serial]) -> list[list[bool]]:
    ret = [[False] * 8] * 8

    for i in reeds:
        i.write(bytearray([1]))

    for (i, serial) in enumerate(reeds):
        x = serial.read(2)

        for j in range(7):
            pos = position_map[i][j]
            if pos[0] < 0:
                continue
            ret[pos[0]][pos[1]] = x[0] >> (6 - i) % 2

        for j in range(6):
            pos = position_map[i][j + 7]
            if pos[0] < 0:
                continue
            ret[pos[0]][pos[1]] = x[0] >> (5 - i) % 2

    return ret


def pos_tuple_to_chess_pos(x, y):
    return chr(x + 97) + chr(y + 49)


def comp_reed(before: list[list[bool]], after: list[list[bool]]):
    before_true = []
    after_true = []
    for i in range(8):
        for j in range(8):
            if before[i][j] != after[i][j]:
                if before[i][j]:
                    before_true.append((i, j))
                else:
                    after_true.append((i, j))

    if len(before_true) == 1:
        before_pos = pos_tuple_to_chess_pos(before_true[0][0], before_true[0][1])
        after_pos = pos_tuple_to_chess_pos(after_true[0][0], after_true[0][1])
        return before_pos + after_pos
    elif len(before_true) == 2:  # check for castling
        if (4, 0) in before_true:  # white king
            if (0, 0) in before_true and (2, 0) in after_true and (3, 0) in after_true:  # white queen side castling
                return "e1c1"
            elif (7, 0) in before_true and (5, 0) in after_true and (6, 0) in after_true:  # white king side castling
                return "e1g1"
        elif (4, 7) in before_true:  # black king
            if (0, 7) in before_true and (2, 7) in after_true and (3, 7) in after_true:  # black queen side castling
                return "e8c8"
            elif (7, 7) in before_true and (5, 7) in after_true and (6, 7) in after_true:  # black king side castling
                return "e8g8"

    return None
