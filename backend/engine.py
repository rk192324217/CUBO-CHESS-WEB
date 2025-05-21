import time
import random
import chess
def evaluate_move(board, move):
    temp_board = board.copy()
    temp_board.push(move)
    return evaluate(temp_board)

def get_ai_move(board, difficulty, user_id=None):
    print(f"Getting AI move for difficulty: {difficulty}")
    print("Board FEN:", board.fen())
    if not board.legal_moves:
        print("No legal moves")
        return None

    # Simulate thinking time based on difficulty
    time.sleep({
        'easy': random.uniform(0.1, 0.5),
        'medium': random.uniform(0.3, 1.0),
        'hard': random.uniform(0.5, 1.5)
    }[difficulty])

    if difficulty == "easy":
        if random.random() < 0.3:  # 30% chance to blunder
            worst_move = min(
                board.legal_moves,
                key=lambda m: evaluate_move(board, m)
            )
            return worst_move
        return random.choice(list(board.legal_moves))

    elif difficulty == "medium":
        return minimax_root(board, 2)

    elif difficulty == "hard":
        if len(board.move_stack) < 5:
            opening_move = get_opening_move(board)
            if opening_move and opening_move in board.legal_moves:
                return opening_move
        return minimax_root(board, 3)

    return random.choice(list(board.legal_moves))  # Fallback


def get_opening_move(board):
    openings = {
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w": "e2e4",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b": "e7e5",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b": "f8c5"
    }
    key = ' '.join(board.fen().split(' ')[:2])
    uci = openings.get(key)
    return chess.Move.from_uci(uci) if uci else None


def minimax_root(board, depth):
    print(f"Minimax root called with depth {depth}")
    best_move = None
    best_score = -float('inf')
    
    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, False, -float('inf'), float('inf'))
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move

def minimax(board, depth, is_maximizing, alpha, beta):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    if is_maximizing:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False, alpha, beta)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True, alpha, beta)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def evaluate(board):
    # Material values (scaled for granularity)
    piece_values = {
        chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
        chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
    }

    score = 0

    # Piece-square tables (for positional awareness)
    pst = {
        chess.PAWN: [
            0, 5, 5, 0, 5, 10, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 10, -10, 0, 10, 20, 50, 0,
            0, -20, 0, 20, 25, 30, 50, 0,
            0, -20, 0, 20, 25, 30, 50, 0,
            0, 10, -10, 0, 10, 20, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 5, 5, 0, 5, 10, 50, 0,
        ],
        chess.KNIGHT: [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50,
        ],
        # Add more PSTs later for other pieces
                chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10, 5, 0, 0, 0, 0, 5,-10,
        -10,10,10,10,10,10,10,-10,
        -10, 0,10,10,10,10, 0,-10,
        -10, 5, 5,10,10, 5, 5,-10,
        -10, 0, 5,10,10, 5, 0,-10,
        -10, 0, 0, 0, 0, 0, 0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
        ],
                chess.ROOK: [
        0, 0, 5,10,10, 5, 0, 0,
        -5, 0, 0, 0, 0, 0, 0,-5,
        -5, 0, 0, 0, 0, 0, 0,-5,
        -5, 0, 0, 0, 0, 0, 0,-5,
        -5, 0, 0, 0, 0, 0, 0,-5,
        -5, 0, 0, 0, 0, 0, 0,-5,
        5, 10,10,10,10,10,10, 5,
        0, 0, 0, 0, 0, 0, 0, 0,
        ],
                chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10, 0, 0, 0, 0, 0, 0,-10,
        -10, 0, 5, 5, 5, 5, 0,-10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0,-10,
        -10, 0, 5, 0, 0, 0, 0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20,
        ],
            chess.KING: [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20,
        ]
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]

            # Add position bonus
            pst_bonus = 0
            if piece.piece_type in pst:
                table = pst[piece.piece_type]
                index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                pst_bonus = table[index]

            if piece.color == chess.WHITE:
                score += value + pst_bonus
            else:
                score -= value + pst_bonus

    # Center control bonus
    center = [chess.D4, chess.E4, chess.D5, chess.E5]
    for square in center:
        piece = board.piece_at(square)
        if piece:
            score += 10 if piece.color == chess.WHITE else -10

    return score
