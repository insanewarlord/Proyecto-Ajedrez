import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import chess
import os

# Tamaño de cada celda del tablero
CELL_SIZE = 80
# Colores para resaltar las casillas seleccionadas y las posibles jugadas
HIGHLIGHT_COLOR_SELECTED = "yellow"
HIGHLIGHT_COLOR_MOVE = "blue"
# Clase para representar una versión personalizada del rey
class CustomKing(chess.Piece):
    def __init__(self, color):
        super().__init__(chess.KING, color)
# Clase principal del tablero de ajedrez
class LoseChessBoard:
    def __init__(self, root, canvas, player_color):
        self.root = root
        self.canvas = canvas
        self.board = self.setup_custom_board()
        self.piece_images = self.load_piece_images()
        self.player_color = player_color
        self.ai_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE
        self.current_turn = chess.WHITE  # Inicializa el turno en blanco
        self.selected_square = None # Cuadro seleccionado inicialmente es None
        self.move_counter, self.turn_counter = {}, {}  # Diccionarios vacíos para contadores de movimientos y turnos
        self.draw_chessboard()  # Dibuja el tablero de ajedrez
        self.canvas.bind("<Button-1>", self.on_click) # Vincula el clic izquierdo del mouse al método on_click
    # Configura el tablero con una disposición inicial personalizada
    def setup_custom_board(self):
        board = chess.Board(fen=None)
        # Define las piezas personalizadas y las piezas estándar para el tablero inicial y Usar CustomKing en lugar de chess.KING
        pieces = [chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, CustomKing, chess.BISHOP, chess.KNIGHT, chess.ROOK]
         # Coloca las piezas en sus posiciones iniciales

        for i, piece in enumerate(pieces):
            if piece == CustomKing:
              # Coloca el rey personalizado en las posiciones iniciales de blancas y negras
                board.set_piece_at(chess.square(i, 0), CustomKing(chess.WHITE))
                board.set_piece_at(chess.square(i, 7), CustomKing(chess.BLACK))
            else:
             # Coloca las piezas estándar  en las posiciones iniciales

                board.set_piece_at(chess.square(i, 0), chess.Piece(piece, chess.WHITE))
                board.set_piece_at(chess.square(i, 7), chess.Piece(piece, chess.BLACK))
            # Coloca los peones en las filas de peones

        for i in range(8):
            board.set_piece_at(chess.square(i, 1), chess.Piece(chess.PAWN, chess.WHITE))
            board.set_piece_at(chess.square(i, 6), chess.Piece(chess.PAWN, chess.BLACK))
        return board
     # Carga las imágenes de las piezas
    def load_piece_images(self):
        piece_images = {} # Diccionario para almacenar las imágenes de las piezas
        piezas = ["reina_blanco", "torre_blanco", "alfil_blanco", "caballo_blanco", "peon_blanco", "rey_blanco",
                  "reina_negro", "torre_negro", "alfil_negro", "caballo_negro", "peon_negro", "rey_negro"]
        for pieza in piezas:
                    # Genera el nombre del archivo de imagen a partir del nombre de la pieza

            filename = os.path.join("imágenes", f"{pieza}.png")
            try:
             # Intenta cargar la imagen y redimensionarla a un tamaño específico
                image = ImageTk.PhotoImage(Image.open(filename).resize((CELL_SIZE, CELL_SIZE)))
             # Almacena la imagen cargada en el diccionario de imágenes de piezas
 
                piece_images[pieza] = image
            except FileNotFoundError:
               # Captura el error si el archivo no se encuentra

                print(f"¡Error! No se encontró el archivo {filename}.")
            except Exception as e:
                print(f"¡Error al cargar {filename}: {str(e)}")

        return piece_images  #Devuelve el diccionario completo de imágenes de piezas
    # Dibuja el tablero de ajedrez y las piezas
    def draw_chessboard(self):
        self.canvas.delete("all")
        
        #dibuja el tablero de ajedrez utilizando un bucle que recorre cada casilla del tablero. La casilla se colorea según sea par o impar 
        for i in range(8):
            for j in range(8):
                color = "#8AE5DA" if (i + j) % 2 == 0 else "#FDFEFE"
                self.canvas.create_rectangle(j * CELL_SIZE, i * CELL_SIZE, (j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE, fill=color)
        #Después, recorre cada casilla del tablero y, si hay una pieza en esa casilla, la dibuja en la posición correspondiente. 
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)
                piece_name = self.get_piece_name(piece)
                image = self.piece_images.get(piece_name)
                if image:
                    self.canvas.create_image(col * CELL_SIZE, (7 - row) * CELL_SIZE, anchor=tk.NW, image=image)
        #Si hay una casilla seleccionada, se resalta y se muestran las posibles movidas
        if self.selected_square is not None:
            self.highlight_square(self.selected_square)
            self.highlight_moves(self.selected_square)
    # Devuelve el nombre de la pieza en el formato adecuado para cargar la imagen
    def get_piece_name(self, piece):
        color = 'blanco' if piece.color == chess.WHITE else 'negro'
        piece_type = {chess.QUEEN: 'reina', chess.ROOK: 'torre', chess.BISHOP: 'alfil', chess.KNIGHT: 'caballo', chess.PAWN: 'peon', chess.KING: 'rey'}[piece.piece_type]
        return f"{piece_type}_{color}"
   
    # Maneja los clics del usuario en el tablero
    def on_click(self, event):
        #  Verifica si es el turno del jugador
        if self.current_turn != self.player_color:
            return
        #  Convierte las coordenadas del clic en una casilla del tablero de ajedrez
        col, row = event.x // CELL_SIZE, 7 - (event.y // CELL_SIZE)
        square = chess.square(col, row)
        #  Si no hay una casilla seleccionada
        if self.selected_square is None:
           # Verifica si la casilla contiene una pieza del jugador
            if self.board.piece_at(square) and self.board.piece_at(square).color == self.current_turn:
                self.selected_square = square
                self.draw_chessboard()   # Redibuja el tablero para mostrar la selección
   
        else:
        #  Si hay una casilla seleccionada, intenta mover la pieza seleccionada a la nueva casilla
            move = chess.Move(self.selected_square, square)
        #  Verifica la legalidad del movimiento
            if move in self.board.legal_moves:
                #  Si el movimiento es legal, lo ejecuta
                self.board.push(move)
                self.selected_square = None
                self.update_move_counter(move)
                self.update_turn_counter()
                self.draw_chessboard()
                self.current_turn = not self.current_turn
                #  Verifica si todas las piezas han sido capturadas
                if self.is_all_pieces_captured():
                    self.handle_game_over() # Maneja el final del juego
                else:
                #  Si el juego no ha terminado, pasa el turno a la IA después de un breve retraso
                    self.root.after(1000, self.make_ai_move)
                # Si el movimiento no es legal, deselecciona la casilla y redibuja el tablero
            else:
                self.selected_square = None
                self.draw_chessboard()
    # Realiza un movimiento de la IA
    def make_ai_move(self):
    #Calcula el mejor movimiento para la IA
        move = self.get_best_move(self.board, self.ai_color)
    #  Si hay un movimiento válido, lo ejecuta
        if move:
            self.board.push(move)
            self.update_move_counter(move)
            self.update_turn_counter()
            self.draw_chessboard()
            self.current_turn = not self.current_turn
        #  Cambia el turno al jugador humano si el juego no ha terminado
            if self.board.is_game_over() or self.is_all_pieces_captured():
                self.handle_game_over()
     # Devuelve los movimientos legales sin incluir movimientos que pondrían al jugador en jaque
    def get_legal_moves_no_check(self, board):
            #  Guarda el estado original del turno del tablero
        original_turn = board.turn
         # Cambia el turno del tablero para simular el turno del oponente
        board.turn = not original_turn
        # Obtiene los movimientos legales del oponente
        opponent_legal_moves = set(move.to_square for move in board.legal_moves)
    # Restaura el estado original del turno del tablero
        board.turn = original_turn
    # Retorna los movimientos legales que no conducen al oponente a una posición donde el jugador esté en jaque
        return [move for move in board.legal_moves if move.to_square not in opponent_legal_moves]
     # Elige el peor movimiento basado en la captura de la pieza de mayor valor
    def choose_worst_move(self, legal_moves):
        # Define una función interna para asignar un valor a cada tipo de pieza
        def piece_value(piece):
            return {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 5, chess.KING: 0}[piece.piece_type]
        #  Inicializa las variables para almacenar el peor movimiento y el valor máximo de la pieza capturada
        worst_move, max_value = None, -1
        #  Itera sobre los movimientos legales
        for move in legal_moves:
        # Obtiene la pieza en la casilla a la que se mueve el movimiento
            piece = self.board.piece_at(move.to_square)
        # Evalúa el valor de la pieza capturada
            value = piece_value(piece) if piece else 0
        # Actualiza el peor movimiento y el valor máximo si se encuentra una pieza de mayor valor
            if value > max_value:
                worst_move, max_value = move, value
        # Retorna el peor movimiento encontrado
        return worst_move
    # Actualiza el contador de movimientos
    def update_move_counter(self, move):
    # Obtiene la pieza en la casilla a la que se mueve el movimiento
        piece = self.board.piece_at(move.to_square)
    #  Si la pieza existe, actualiza el contador de movimientos para esa pieza
        if piece:
            key = self.get_piece_name(piece)
            self.move_counter[key] = self.move_counter.get(key, 0) + 1
    # Actualiza el contador de turnos
    def update_turn_counter(self):
    #  Determina el color del jugador actual (Blanco o Negro)
        turn = "Blanco" if self.current_turn == chess.WHITE else "Negro"
    #  Incrementa el contador de turnos para ese color en el diccionario `turn_counter`
        self.turn_counter[turn] = self.turn_counter.get(turn, 0) + 1
    # Verifica si todas las piezas (excepto los reyes) han sido capturadas
    def is_all_pieces_captured(self):
    # Comprueba si hay alguna pieza que no sea un rey en el tablero
        return not any(piece for piece in self.board.piece_map().values() if piece.piece_type != chess.KING)
    # Resalta la casilla seleccionada
    def highlight_square(self, square):
        col, row = chess.square_file(square), chess.square_rank(square)
        self.canvas.create_rectangle(col * CELL_SIZE, (7 - row) * CELL_SIZE, (col + 1) * CELL_SIZE, (8 - row) * CELL_SIZE, outline=HIGHLIGHT_COLOR_SELECTED, width=3)
    # Resalta las posibles jugadas desde una casilla seleccionada
    def highlight_moves(self, square):
    # Obtiene todos los movimientos legales en el tablero
        legal_moves = self.board.legal_moves
    # Itera sobre los movimientos legales
        for move in legal_moves:
        # Verifica si el movimiento comienza desde la casilla dada
            if move.from_square == square:
            # Obtiene la casilla destino del movimiento
                to_square = move.to_square
                col, row = chess.square_file(to_square), chess.square_rank(to_square)
            # Dibujar un rectángulo alrededor de la casilla destino del movimiento
                self.canvas.create_rectangle(col * CELL_SIZE, (7 - row) * CELL_SIZE, (col + 1) * CELL_SIZE, (8 - row) * CELL_SIZE, outline=HIGHLIGHT_COLOR_MOVE, width=3)
    # Implementación del algoritmo minimax con poda alfa-beta
    def minimax(self, depth, board, is_maximizing, alpha, beta):
    # Condición de parada: alcanza la profundidad máxima o el juego ha terminado
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)
    # Obtener todos los movimientos legales sin poner en jaque al oponente
        legal_moves = list(self.get_legal_moves_no_check(board))

        if is_maximizing:
        # Inicializar el valor mínimo para el jugador maximizador
            min_eval = float('inf')
            for move in legal_moves:
            # Realizar el movimiento
                board.push(move)
            # Llamar recursivamente a minimax para el siguiente nivel (minimizando)
                eval = self.minimax(depth - 1, board, False, alpha, beta)
            # Deshacer el movimiento
                board.pop()
            # Actualizar el valor mínimo
                min_eval = min(min_eval, eval)
            # Actualizar el valor beta para la poda alfa-beta
                beta = min(beta, eval)
            # Realizar la poda alfa-beta si es posible
                if beta <= alpha:
                    break
            return min_eval
        else:
        # Inicializar el valor máximo para el jugador minimizador
            max_eval = float('-inf')
            for move in legal_moves:
            # Realizar el movimiento
                board.push(move)
            # Llamar recursivamente a minimax para el siguiente nivel (maximizando)
                eval = self.minimax(depth - 1, board, True, alpha, beta)
            # Deshacer el movimiento
                board.pop()
            # Actualizar el valor máximo
                max_eval = max(max_eval, eval)
            # Actualizar el valor alfa para la poda alfa-beta
                alpha = max(alpha, eval)
            # Realizar la poda alfa-beta si es posible
                if beta <= alpha:
                    break
            return max_eval
    # Obtiene el mejor movimiento basado en el algoritmo minimax
    def get_best_move(self, board, color):
        best_move = None
    # Inicializar el mejor valor como infinito negativo para el jugador negro y como infinito positivo para el jugador blanco
        best_value = float('inf') if color == chess.WHITE else float('-inf')
    # Iterar sobre todos los movimientos legales disponibles
        for move in self.get_legal_moves_no_check(board):
        # Realizar el movimiento
            board.push(move)
        # Llamar a minimax para evaluar el estado del tablero después del movimiento
            board_value = self.minimax(3, board, color == chess.WHITE, float('-inf'), float('inf'))
        # Deshacer el movimiento
            board.pop()
        # Actualizar el mejor movimiento si el valor del tablero es mejor que el mejor valor actual
            if (color == chess.WHITE and board_value < best_value) or (color == chess.BLACK and board_value > best_value):
                best_value = board_value
                best_move = move
        return best_move
    # Maneja el final del juego
    def handle_game_over(self):
        winner = Determine_winner(self.board, self.move_counter)
        if winner:
           messagebox.showinfo("Fin del juego", f"¡{winner} gana!")
        else:
          messagebox.showinfo("Fin del juego", "¡Juego terminado!")
        self.root.quit()

    # Evalúa el tablero asignando valores a las piezas
    def evaluate_board(self, board):
    # Valores de las piezas
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 5,
            chess.KING: 0
        }
    # Inicializar la puntuación de la evaluación
        evaluation = 0
    # Iterar sobre todas las casillas del tablero
        for square in chess.SQUARES:
        # Obtener la pieza en la casilla actual
            piece = board.piece_at(square)
            if piece:
            # Obtener el valor de la pieza según el tipo
                value = piece_values[piece.piece_type]
            # Sumar o restar el valor dependiendo del color de la pieza
                evaluation += value if piece.color == chess.WHITE else -value
        return evaluation
    def Determine_winner(board, move_counter):
    # Contadores de piezas capturadas por cada jugador
        white_captured = move_counter.get('peon_negro', 0) + move_counter.get('alfil_negro', 0) + move_counter.get('caballo_negro', 0) + move_counter.get('torre_negro', 0) + move_counter.get('reina_negro', 0)
        black_captured = move_counter.get('peon_blanco', 0) + move_counter.get('alfil_blanco', 0) + move_counter.get('caballo_blanco', 0) + move_counter.get('torre_blanco', 0) + move_counter.get('reina_blanco', 0)

    # Si solo queda una pieza en el tablero
        if sum(1 for _ in board.piece_map()) == 2:
        # Determina al ganador según la cantidad de piezas capturadas
            if white_captured < black_captured:
               return "Blancas"
            elif black_captured < white_captured:
               return "Negras"
            else:
               return "Empate"
        else:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ajedrez - Modo Humano vs IA")

    canvas = tk.Canvas(root, width=8 * CELL_SIZE, height=8 * CELL_SIZE)
    canvas.pack()

    player_color = chess.WHITE
    app = LoseChessBoard(root, canvas, player_color)

    root.mainloop()
