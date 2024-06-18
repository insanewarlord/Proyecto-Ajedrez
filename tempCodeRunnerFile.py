                piece_name = self.get_piece_name(piece)
                image = self.piece_images.get(piece_name)
                if image:
                    self.canvas.create_image(col * CELL_SIZE, (7 - row) * CELL_SIZE, anchor=tk.NW, image=image)
        # Si hay una casilla seleccionada, se resalta y se muestran las posibles jugadas
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
        # Verifica si es el turno del jugador
        if self.current_turn != self.player_color:
            return
        # Convierte las coordenadas del clic en una casilla del tablero de ajedrez
        col, row = event.x // CELL_SIZE, 7 - (event.y // CELL_SIZE)
        square = chess.square(col, row)
        # Si no hay una casilla seleccionada
        if self.selected_square is None:
            # Verifica si la casilla contiene una pieza del jugador
            if self.board.piece_at(square) and self.board.piece_at(square).color == self.current_turn:
                self.selected_square = square
                self.draw_chessboard()  # Redibuja el tablero para mostrar la selección
        else:
            # Si hay una casilla seleccionada, intenta mover la pieza seleccionada a la nueva casilla
            move = chess.Move(self.selected_square, square)
            # Verifica la legalidad del movimiento
            if move in self.board.legal_moves:
                # Si el movimiento es legal, lo ejecuta
                self.board.push(move)
                self.selected_square = None
                self.update_move_counter(move)
                self.update_turn_counter()
                self.draw_chessboard()
                self.current_turn = not self.current_turn
                # Verifica si solo quedan los reyes en el tablero
                if self.is_only_kings_left():
                    self.handle_game_over()  # Maneja el final del juego
                else:
                    # Si el juego no ha terminado, pasa el turno a la IA después de un breve retraso
                    self.root.after(1000, self.make_ai_move)
            else:
                # Si el movimiento no es legal, deselecciona la casilla y redibuja el tablero
                self.selected_square = None
                self.draw_chessboard()

    # Realiza un movimiento de la IA
    def make_ai_move(self):
        # Calcula el mejor movimiento para la IA
        move = self.get_best_move(self.board, self.ai_color)
        # Si hay un movimiento válido, lo ejecuta
        if move:
            self.board.push(move)
            self.update_move_counter(move)
            self.update_turn_counter()
            self.draw_chessboard()
            self.current_turn = not self.current_turn
            # Cambia el turno al jugador humano si el juego no ha terminado
            if self.board.is_game_over() or self.is_only_kings_left():
                self.handle_game_over()

    # Devuelve los movimientos legales sin incluir movimientos que pondrían al jugador en jaque
    def get_legal_moves_no_check(self, board):
        # Guarda el estado original del turno del tablero
        original_turn = board.turn
        # Cambia el turno del tablero para simular el turno del oponente
        board.turn = not original_turn
        # Obtiene los movimientos legales del oponente
        opponent_legal_moves = set(move.to_square for move in board.legal_moves)
        # Restaura el estado original del turno del tablero
        board.turn = original_turn
        # Retorna los movimientos legales que no dejarían al jugador en jaque
        return [move for move in board.legal_moves if move.to_square not in opponent_legal_moves]

    # Función para evaluar el mejor movimiento para la IA
    def get_best_move(self, board, color):
        legal_moves = self.get_legal_moves_no_check(board)
        # Si no hay movimientos legales, retorna None
        if not legal_moves:
            return None
        # Si hay movimientos legales, selecciona uno al azar
        move = legal_moves[0]
        return move

    # Resalta una casilla en el tablero
    def highlight_square(self, square):
        row, col = divmod(square, 8)
        self.canvas.create_rectangle(col * CELL_SIZE, (7 - row) * CELL_SIZE, (col + 1) * CELL_SIZE, (7 - row + 1) * CELL_SIZE, outline=HIGHLIGHT_COLOR_SELECTED, width=3)

    # Resalta las posibles jugadas para una casilla seleccionada
    def highlight_moves(self, square):
        legal_moves = self.board.legal_moves
        for move in legal_moves:
            if move.from_square == square:
                row, col = divmod(move.to_square, 8)
                self.canvas.create_rectangle(col * CELL_SIZE, (7 - row) * CELL_SIZE, (col + 1) * CELL_SIZE, (7 - row + 1) * CELL_SIZE, outline=HIGHLIGHT_COLOR_MOVE, width=3)

    # Muestra un mensaje de finalización del juego
    def handle_game_over(self):
        # Verifica el resultado del juego y muestra el mensaje correspondiente
        if self.is_only_kings_left():
            message = "¡Juego terminado! Solo quedan los reyes."
        elif self.board.is_checkmate():
            winner = "Blancas" if self.board.turn == chess.BLACK else "Negras"
            message = f"¡{winner} han hecho jaque mate!"
        elif self.board.is_stalemate():
            message = "¡Empate por ahogado!"
        else:
            message = "¡Juego terminado!"
        messagebox.showinfo("Fin del juego", message)

    # Verifica si solo quedan los reyes en el tablero
    def is_only_kings_left(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.piece_type != chess.KING:
                return False
        return True

    # Actualiza el contador de movimientos para cada pieza
    def update_move_counter(self, move):
        piece = self.board.piece_at(move.to_square)
        if piece:
            self.move_counter[piece.symbol()] = self.move_counter.get(piece.symbol(), 0) + 1

    # Actualiza el contador de turnos
    def update_turn_counter(self):
        self.turn_counter[self.board.turn] = self.turn_counter.get(self.board.turn, 0) + 1


# Configuración de la interfaz gráfica
def main():
    root = tk.Tk()
    root.title("Lose Chess")
    canvas = tk.Canvas(root, width=8 * CELL_SIZE, height=8 * CELL_SIZE)
    canvas.pack()
    player_color = chess.WHITE  # O chess.BLACK si el jugador elige negras
    LoseChessBoard(root, canvas, player_color)
    root.mainloop()

if __name__ == "__main__":
    main()
