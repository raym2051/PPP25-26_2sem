import pygame
import sys

# ШАХМАТНЫЕ ФИГУРЫ

class Piece:
    """Базовый класс для всех фигур."""
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.symbol = '?'

    def get_possible_moves(self, board, en_passant_target=None):
        return []

    def __repr__(self):
        return self.symbol


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'P' if color == 'white' else 'p'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        direction = 1 if self.color == 'white' else -1

        new_row = row + direction
        if 0 <= new_row < 8 and board.get_piece(new_row, col) is None:
            moves.append((new_row, col))
            if (self.color == 'white' and row == 1) or (self.color == 'black' and row == 6):
                two_row = row + 2 * direction
                if board.get_piece(two_row, col) is None:
                    moves.append((two_row, col))

        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_col < 8:
                new_row = row + direction
                if 0 <= new_row < 8:
                    target = board.get_piece(new_row, new_col)
                    if target and target.color != self.color:
                        moves.append((new_row, new_col))

        if en_passant_target and (en_passant_target == (row + direction, col + 1) or
                                  en_passant_target == (row + direction, col - 1)):
            moves.append(en_passant_target)

        return moves


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'R' if color == 'white' else 'r'
        self.has_moved = False

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'N' if color == 'white' else 'n'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves


class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'B' if color == 'white' else 'b'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'Q' if color == 'white' else 'q'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'K' if color == 'white' else 'k'
        self.has_moved = False

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board.get_piece(r, c)
                    if target is None or target.color != self.color:
                        moves.append((r, c))
        # Рокировка (упрощённо, без проверки шахов)
        if not self.has_moved:
            rook_short = board.get_piece(row, 7)
            if rook_short and isinstance(rook_short, Rook) and not rook_short.has_moved:
                if all(board.get_piece(row, c) is None for c in range(col+1, 7)):
                    moves.append((row, col+2))
            rook_long = board.get_piece(row, 0)
            if rook_long and isinstance(rook_long, Rook) and not rook_long.has_moved:
                if all(board.get_piece(row, c) is None for c in range(1, col)):
                    moves.append((row, col-2))
        return moves


# НОВЫЕ ОРИГИНАЛЬНЫЕ ФИГУРЫ 

class Griffin(Piece):
    """Грифон: ходит как слон ИЛИ как конь."""
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'G' if color == 'white' else 'g'

    def get_possible_moves(self, board, en_passant_target=None):
        bishop_moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        row, col = self.position
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None:
                    bishop_moves.append((r, c))
                else:
                    if target.color != self.color:
                        bishop_moves.append((r, c))
                    break
                r += dr
                c += dc

        knight_moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    knight_moves.append((r, c))

        return bishop_moves + knight_moves


class Camel(Piece):
    """Верблюд: ходит на (3,1) и (1,3)."""
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'C' if color == 'white' else 'c'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        offsets = [(-3, -1), (-3, 1), (-1, -3), (-1, 3), (1, -3), (1, 3), (3, -1), (3, 1)]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves


class Elephant(Piece):
    """Слон: ходит на две клетки в любом направлении (включая диагонали и ортогональ),
       перепрыгивая через любую фигуру на первой клетке."""
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'E' if color == 'white' else 'e'

    def get_possible_moves(self, board, en_passant_target=None):
        moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        for dr, dc in directions:
            r2, c2 = row + 2*dr, col + 2*dc
            if 0 <= r2 < 8 and 0 <= c2 < 8:
                target = board.get_piece(r2, c2)
                if target is None or target.color != self.color:
                    moves.append((r2, c2))
        return moves



class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def place_piece(self, piece, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            piece.position = (row, col)

    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def move_piece(self, start, end):
        piece = self.get_piece(*start)
        if piece is None:
            return False
        self.board[start[0]][start[1]] = None
        self.place_piece(piece, end[0], end[1])
        return True


class Move:
    def __init__(self, start, end, piece, captured_piece=None, is_castling=False,
                 rook_start=None, rook_end=None, is_en_passant=False, en_passant_capture_pos=None):
        self.start = start
        self.end = end
        self.piece = piece
        self.captured_piece = captured_piece
        self.is_castling = is_castling
        self.rook_start = rook_start
        self.rook_end = rook_end
        self.is_en_passant = is_en_passant
        self.en_passant_capture_pos = en_passant_capture_pos

    def execute(self, board):
        board.board[self.start[0]][self.start[1]] = None
        board.board[self.end[0]][self.end[1]] = self.piece
        self.piece.position = self.end

        if self.is_en_passant and self.en_passant_capture_pos:
            captured = board.get_piece(*self.en_passant_capture_pos)
            if captured:
                board.board[self.en_passant_capture_pos[0]][self.en_passant_capture_pos[1]] = None
                self.captured_piece = captured

        if self.is_castling and self.rook_start and self.rook_end:
            rook = board.get_piece(*self.rook_start)
            if rook:
                board.board[self.rook_start[0]][self.rook_start[1]] = None
                board.board[self.rook_end[0]][self.rook_end[1]] = rook
                rook.position = self.rook_end

    def undo(self, board):
        board.board[self.start[0]][self.start[1]] = self.piece
        self.piece.position = self.start
        board.board[self.end[0]][self.end[1]] = self.captured_piece
        if self.captured_piece:
            self.captured_piece.position = self.end

        if self.is_en_passant and self.en_passant_capture_pos:
            board.board[self.en_passant_capture_pos[0]][self.en_passant_capture_pos[1]] = self.captured_piece
            if self.captured_piece:
                self.captured_piece.position = self.en_passant_capture_pos

        if self.is_castling and self.rook_start and self.rook_end:
            rook = board.get_piece(*self.rook_end)
            if rook:
                board.board[self.rook_end[0]][self.rook_end[1]] = None
                board.board[self.rook_start[0]][self.rook_start[1]] = rook
                rook.position = self.rook_start


class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'
        self.en_passant_target = None
        self.game_over = False
        self.winner = None
        self.setup_board()

    def setup_board(self):
        # Пешки
        for col in range(8):
            self.board.place_piece(Pawn('white', (1, col)), 1, col)
            self.board.place_piece(Pawn('black', (6, col)), 6, col)
        # Ладьи
        self.board.place_piece(Rook('white', (0, 0)), 0, 0)
        self.board.place_piece(Rook('white', (0, 7)), 0, 7)
        self.board.place_piece(Rook('black', (7, 0)), 7, 0)
        self.board.place_piece(Rook('black', (7, 7)), 7, 7)
        # Кони
        self.board.place_piece(Knight('white', (0, 1)), 0, 1)
        self.board.place_piece(Knight('white', (0, 6)), 0, 6)
        self.board.place_piece(Knight('black', (7, 1)), 7, 1)
        self.board.place_piece(Knight('black', (7, 6)), 7, 6)
        # Новые фигуры вместо слонов
        self.board.place_piece(Griffin('white', (0, 2)), 0, 2)
        self.board.place_piece(Elephant('white', (0, 5)), 0, 5)
        self.board.place_piece(Elephant('black', (7, 2)), 7, 2)
        self.board.place_piece(Camel('black', (7, 5)), 7, 5)
        # Ферзи
        self.board.place_piece(Queen('white', (0, 3)), 0, 3)
        self.board.place_piece(Queen('black', (7, 3)), 7, 3)
        # Короли
        self.board.place_piece(King('white', (0, 4)), 0, 4)
        self.board.place_piece(King('black', (7, 4)), 7, 4)

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color and isinstance(piece, King):
                    return (row, col)
        return None

    def is_square_attacked(self, row, col, friendly_color):
        opponent = 'black' if friendly_color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == opponent:
                    if isinstance(piece, Pawn):
                        direction = 1 if piece.color == 'white' else -1
                        if (row, col) == (r + direction, c + 1) or (row, col) == (r + direction, c - 1):
                            return True
                    else:
                        moves = piece.get_possible_moves(self.board)
                        if (row, col) in moves:
                            return True
        return False

    def get_attacked_squares(self, color):
        attacked = set()
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color:
                    if isinstance(piece, Pawn):
                        direction = 1 if piece.color == 'white' else -1
                        for dc in (-1, 1):
                            r = row + direction
                            c = col + dc
                            if 0 <= r < 8 and 0 <= c < 8:
                                attacked.add((r, c))
                    elif isinstance(piece, King):
                        for dr in (-1, 0, 1):
                            for dc in (-1, 0, 1):
                                if dr == 0 and dc == 0:
                                    continue
                                r = row + dr
                                c = col + dc
                                if 0 <= r < 8 and 0 <= c < 8:
                                    attacked.add((r, c))
                    else:
                        moves = piece.get_possible_moves(self.board)
                        for move in moves:
                            attacked.add(move)
        return attacked

    def is_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        return self.is_square_attacked(*king_pos, color)

    def is_valid_move(self, move):
        piece = move.piece
        start = move.start
        end = move.end

        if isinstance(piece, Pawn):
            possible = piece.get_possible_moves(self.board, self.en_passant_target)
        else:
            possible = piece.get_possible_moves(self.board)

        if end not in possible:
            return False

        test_move = Move(start, end, piece,
                         captured_piece=self.board.get_piece(*end),
                         is_castling=move.is_castling,
                         rook_start=move.rook_start,
                         rook_end=move.rook_end,
                         is_en_passant=move.is_en_passant,
                         en_passant_capture_pos=move.en_passant_capture_pos)
        test_move.execute(self.board)

        in_check = self.is_check(self.current_turn)

        test_move.undo(self.board)

        return not in_check

    def has_legal_moves(self, color):
        """Проверяет, есть ли у игрока хотя бы один допустимый ход."""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color:
                    if isinstance(piece, Pawn):
                        possible = piece.get_possible_moves(self.board, self.en_passant_target)
                    else:
                        possible = piece.get_possible_moves(self.board)
                    for end in possible:
                        is_castling = isinstance(piece, King) and abs(end[1] - col) == 2
                        rook_start = rook_end = None
                        if is_castling:
                            if end[1] > col:
                                rook_start = (row, 7)
                                rook_end = (row, 5)
                            else:
                                rook_start = (row, 0)
                                rook_end = (row, 3)
                        is_en_passant = False
                        en_passant_capture_pos = None
                        captured = self.board.get_piece(*end)
                        if isinstance(piece, Pawn):
                            if self.en_passant_target and end == self.en_passant_target:
                                enemy_pawn_pos = (row, end[1])
                                enemy_pawn = self.board.get_piece(*enemy_pawn_pos)
                                if enemy_pawn and isinstance(enemy_pawn, Pawn) and enemy_pawn.color != color:
                                    is_en_passant = True
                                    en_passant_capture_pos = enemy_pawn_pos
                                    captured = enemy_pawn
                        move = Move((row, col), end, piece, captured, is_castling,
                                    rook_start, rook_end, is_en_passant, en_passant_capture_pos)
                        if self.is_valid_move(move):
                            return True
        return False

    def is_checkmate(self, color):
        return self.is_check(color) and not self.has_legal_moves(color)

    def make_move(self, start, end):
        if self.game_over:
            return False

        piece = self.board.get_piece(*start)
        if piece is None or piece.color != self.current_turn:
            return False

        is_castling = isinstance(piece, King) and abs(end[1] - start[1]) == 2
        rook_start = rook_end = None
        if is_castling:
            row = start[0]
            if end[1] > start[1]:
                rook_start = (row, 7)
                rook_end = (row, 5)
            else:
                rook_start = (row, 0)
                rook_end = (row, 3)

        is_en_passant = False
        en_passant_capture_pos = None
        captured = self.board.get_piece(*end)
        if isinstance(piece, Pawn):
            if self.en_passant_target and end == self.en_passant_target:
                enemy_pawn_pos = (start[0], end[1])
                enemy_pawn = self.board.get_piece(*enemy_pawn_pos)
                if enemy_pawn and isinstance(enemy_pawn, Pawn) and enemy_pawn.color != self.current_turn:
                    is_en_passant = True
                    en_passant_capture_pos = enemy_pawn_pos
                    captured = enemy_pawn

        move = Move(start, end, piece, captured, is_castling,
                    rook_start, rook_end, is_en_passant, en_passant_capture_pos)

        if not self.is_valid_move(move):
            return False

        move.execute(self.board)

        if isinstance(piece, (King, Rook)):
            piece.has_moved = True
        if is_castling and rook_start:
            rook = self.board.get_piece(*rook_end)
            if rook:
                rook.has_moved = True

        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(end[0] - start[0]) == 2:
            self.en_passant_target = ((start[0] + end[0]) // 2, start[1])

        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            self.board.place_piece(Queen(piece.color, end), end[0], end[1])

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        if self.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = 'white' if self.current_turn == 'black' else 'black'

        return True

    def promote_pawn(self, pos, piece_type):
        pawn = self.board.get_piece(*pos)
        if not pawn or not isinstance(pawn, Pawn):
            return False
        color = pawn.color
        if piece_type == 'Q':
            new_piece = Queen(color, pos)
        elif piece_type == 'R':
            new_piece = Rook(color, pos)
        elif piece_type == 'B':
            new_piece = Bishop(color, pos)
        elif piece_type == 'N':
            new_piece = Knight(color, pos)
        else:
            return False
        self.board.place_piece(new_piece, pos[0], pos[1])
        return True


# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС

WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // 8
COLOR_WHITE = (240, 217, 181)
COLOR_BLACK = (181, 136, 99)
COLOR_HIGHLIGHT = (186, 202, 68)
COLOR_POSSIBLE = (100, 200, 100, 100)
COLOR_ATTACKED = (255, 0, 0)        # для фигур под ударом
COLOR_CAPTURE = (255, 100, 0)       # для фигур, которые можно взять выбранной

UNICODE_PIECES = {
    ('white', 'K'): '♔', ('white', 'Q'): '♕', ('white', 'R'): '♖',
    ('white', 'B'): '♗', ('white', 'N'): '♘', ('white', 'P'): '♙',
    ('white', 'G'): 'G', ('white', 'C'): 'C', ('white', 'E'): 'E',
    ('black', 'K'): '♚', ('black', 'Q'): '♛', ('black', 'R'): '♜',
    ('black', 'B'): '♝', ('black', 'N'): '♞', ('black', 'P'): '♟',
    ('black', 'G'): 'g', ('black', 'C'): 'c', ('black', 'E'): 'e',
}

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Шахматы с новыми фигурами")
        self.game = Game()
        self.selected_pos = None
        self.possible_moves = []
        self.running = True
        self.waiting_for_promotion = False
        self.promotion_pos = None

        font_candidates = ["Apple Symbols", "Arial Unicode MS", "DejaVu Sans",
                           "Segoe UI Symbol", "Noto Sans Symbols2", "Arial"]
        found_font = None
        for name in font_candidates:
            try:
                font = pygame.font.SysFont(name, CELL_SIZE - 20)
                test = font.render("♔", True, (0, 0, 0))
                if test.get_width() > 0:
                    found_font = font
                    break
            except:
                continue
        if found_font is None:
            found_font = pygame.font.Font(None, CELL_SIZE - 20)
        self.font = found_font
        self.message_font = pygame.font.SysFont("Arial", 36)

    def draw_board(self):
        # Вычисляем клетки, атакуемые противником (для подсветки фигур текущего игрока под ударом)
        opponent = 'black' if self.game.current_turn == 'white' else 'white'
        attacked_squares = self.game.get_attacked_squares(opponent)

        # Если выбрана фигура, определяем вражеские фигуры, которые можно взять
        capture_targets = set()
        if self.selected_pos is not None:
            piece = self.game.board.get_piece(*self.selected_pos)
            if piece:
                if isinstance(piece, Pawn):
                    moves = piece.get_possible_moves(self.game.board, self.game.en_passant_target)
                else:
                    moves = piece.get_possible_moves(self.game.board)
                # Ходы, которые ведут на вражескую фигуру
                for move in moves:
                    target_piece = self.game.board.get_piece(*move)
                    if target_piece and target_piece.color != self.game.current_turn:
                        capture_targets.add(move)

        for row in range(8):
            for col in range(8):
                color = COLOR_WHITE if (row + col) % 2 == 0 else COLOR_BLACK
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)

                # Подсветка выбранной клетки
                if self.selected_pos == (row, col):
                    pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect)
                # Подсветка возможных ходов
                if (row, col) in self.possible_moves:
                    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    s.fill(COLOR_POSSIBLE)
                    self.screen.blit(s, rect)

        # Рисуем фигуры
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece:
                    piece_type = piece.__class__.__name__
                    if piece_type == 'King':
                        sym = 'K'
                    elif piece_type == 'Queen':
                        sym = 'Q'
                    elif piece_type == 'Rook':
                        sym = 'R'
                    elif piece_type == 'Bishop':
                        sym = 'B'
                    elif piece_type == 'Knight':
                        sym = 'N'
                    elif piece_type == 'Pawn':
                        sym = 'P'
                    elif piece_type == 'Griffin':
                        sym = 'G'
                    elif piece_type == 'Camel':
                        sym = 'C'
                    elif piece_type == 'Elephant':
                        sym = 'E'
                    else:
                        sym = '?'
                    char = UNICODE_PIECES.get((piece.color, sym), '?')
                    text = self.font.render(char, True, (0, 0, 0))
                    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)

        # Подсветка фигур под ударом (для текущего игрока)
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece and piece.color == self.game.current_turn:
                    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    # Шах короля
                    if isinstance(piece, King) and self.game.is_check(self.game.current_turn):
                        pygame.draw.rect(self.screen, COLOR_ATTACKED, rect, 4)
                    # Обычная фигура под ударом
                    elif (row, col) in attacked_squares:
                        pygame.draw.rect(self.screen, COLOR_ATTACKED, rect, 2)
                    # Если фигура может быть взята выбранной фигурой
                    if (row, col) in capture_targets:
                        pygame.draw.rect(self.screen, COLOR_CAPTURE, rect, 2)

        if self.game.game_over:
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            winner_text = f"{self.game.winner.capitalize()} wins by checkmate!"
            text = self.message_font.render(winner_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            self.screen.blit(text, text_rect)

    def get_square_under_mouse(self):
        x, y = pygame.mouse.get_pos()
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game.game_over:
                if event.type == pygame.KEYDOWN:
                    self.running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.waiting_for_promotion:
                    mouse_pos = pygame.mouse.get_pos()
                    panel_width = 300
                    panel_height = 80
                    panel_x = (WINDOW_SIZE - panel_width) // 2
                    panel_y = (WINDOW_SIZE - panel_height) // 2
                    button_width = 60
                    button_height = 60
                    spacing = (panel_width - 4 * button_width) // 5
                    pieces = [('Q', '♕'), ('R', '♖'), ('B', '♗'), ('N', '♘')]
                    for i, (piece_char, symbol) in enumerate(pieces):
                        x = panel_x + spacing + i * (button_width + spacing)
                        y = panel_y + (panel_height - button_height) // 2
                        rect = pygame.Rect(x, y, button_width, button_height)
                        if rect.collidepoint(mouse_pos):
                            self.game.promote_pawn(self.promotion_pos, piece_char)
                            self.waiting_for_promotion = False
                            self.promotion_pos = None
                            break
                    return

                pos = self.get_square_under_mouse()
                if pos is None:
                    continue

                if self.selected_pos is None:
                    piece = self.game.board.get_piece(*pos)
                    if piece and piece.color == self.game.current_turn:
                        self.selected_pos = pos
                        if isinstance(piece, Pawn):
                            moves = piece.get_possible_moves(self.game.board, self.game.en_passant_target)
                        else:
                            moves = piece.get_possible_moves(self.game.board)
                        self.possible_moves = moves
                    else:
                        self.selected_pos = None
                        self.possible_moves = []
                else:
                    if pos == self.selected_pos:
                        self.selected_pos = None
                        self.possible_moves = []
                    else:
                        success = self.game.make_move(self.selected_pos, pos)
                        if success:
                            piece = self.game.board.get_piece(*pos)
                            if piece and isinstance(piece, Pawn) and (pos[0] == 0 or pos[0] == 7):
                                self.game.board.place_piece(Pawn(piece.color, pos), pos[0], pos[1])
                                self.promotion_pos = pos
                                self.waiting_for_promotion = True
                            self.selected_pos = None
                            self.possible_moves = []
                        else:
                            self.selected_pos = None
                            self.possible_moves = []

    def run(self):
        while self.running:
            self.handle_events()
            self.draw_board()
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()
