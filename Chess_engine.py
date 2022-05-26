# TSE Chess engine game
from playsound import playsound # playsounds made from gtts
import cv2 # import open CV for piece and board detection



class GState:
    def __init__(self):
        # 8x8 board in a 2D list, each element/space has 2 characters 
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
            # For the board I drew it out as a 2d list and intended to label piece reCgition or empty squares
            # as part of the 2 character 2d array. From attempt with qr codes or using piece classifier

        # Attempt at Piece and board detection with QR codes
        #self.board2 = []
        #for i in range(len(self.board)):
         #   for j in range(len(self.board[i])):
          #      self.board2.append(self.board[i][j])
                #img=cv2.imread("test.png")
                #det=cv2.QRCodeDetector()
                #test, pts, st_code=det.detectAndDecode(img)



        # Access move functions for each piece regardless of colour
        self.moveFunctions = {"p": self.pawn_moves, "R": self.rook_moves,
                              "B": self.bishop_moves,"N": self.knight_moves,
                              "Q": self.queen_moves, "K": self.king_moves}
        self.white_move = True # If white move is False it is black side turn
        self.moveLog = [] #  Move log for undoing moves
        self.white_king_loc = (7, 4)  # self.board white king location
        self.black_king_loc = (0, 4) # self.board black king location
        self.checkmate = False # Checkmate variable to determine if checkmate
        self.stalemate = False # checks for stalemate/draw
        self.in_check = False # checks in anyone is in check
        self.gamestatus = False # used to determine if a check leads to being a checkmate or stalemate
        self.pins = [] #  use a pin array as a way to hold a king in check by use of a pinned piece that cannot move
        self.checks = [] #  checks array

# takes a move as parameter and executes it
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--" #  set old board value to empty
        self.board[move.end_row][move.end_col] = move.piece_moved # set the board location as the piece thats been moved from move
        self.moveLog.append(move) # log the move
        self.white_move = not self.white_move #swap player turn
        #update the king location if moved
        if move.piece_moved == "wK":
            self.white_king_loc = (move.start_row, move.start_col)
        # if black king moved change king location
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)

        # Pawn upgrade
        if move.pawn_upgrade:
            # sets the pawn that reaches end row to a queen as an upgrade if pawn_upgrade True
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

    #undo last move made
    def undo_move(self):
        if len(self.moveLog): #  
            move = self.moveLog.pop() # adds the last move made to move to undo
            self.board[move.start_row][move.start_col] = move.piece_moved # resets board based on previous move
            self.board[move.end_row][move.end_col] = move.piece_taken #  changes piece if taken
            self.white_move = not self.white_move # undoes the users turn side to go back and reset
            # update the king location if moved
            if move.piece_moved == "wK":
                self.white_king_loc = (move.start_row, move.start_col)
            #if moved change king location
            elif move.piece_moved == "bK":
                self.black_king_loc = (move.end_row, move.end_col)

    #all moves considering checks
    def valid_moves(self):
        moves = [] 
        self.in_check, self.pins, self.checks = self.pins_n_checks() #  calls the pin and checks function to give values and game status 
        # sets different king colour row and column to be used later
        if self.white_move:
            kings_row = self.white_king_loc[0]
            kings_col = self.white_king_loc[1]
        else:
            kings_row = self.black_king_loc[0]
            kings_col = self.black_king_loc[1]

        # if someone is in check do the following to check for valid moves to resolve checks
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.possible_moves() # get the possible moves based on piece and locations to move
                #to block a check move piece in between
                check = self.checks[0] # check info
                check_row = check[0] 
                check_col = check[1]
                piece_check = self.board[check_row][check_col] # enemy piece checking player
                valid_sqs = [] # available squares
                # if knight capture night or move king other pieces can be blocked
                if piece_check[1] == "N":
                    valid_sqs = [(check_row, check_col)] 
                else:
                    for i in range(1, 8):
                        valid_sq = (kings_row + check[2] * i, kings_col + check[3] * i) # check directions
                        valid_sqs.append(valid_sq)

                        if valid_sq[0] == check_row and valid_sq[1] == check_col: #piece and end checks
                            break

                # remove moves that dont block check or move the king
                for i in range(len(moves)-1, -1, -1): # go backwards from removing item list
                    if moves[i].piece_moved[1] != "K":
                        if not (moves[i].end_row, moves[i].end_col) in valid_sqs:
                            moves.remove(moves[i])

                # resulting if in check
                if len(moves) == 0 and self.gamestatus: # check for checkmate
                    self.checkmate = True

                # if length of moves is not 0 but check is true play the check sound to let user know they are in check
                if len(moves) !=0 and self.in_check:
                    playsound("checksound.mp3")

            else: # double check king has to move
                self.king_moves(kings_row, kings_col, moves)





        else:# not in check so all moves fine
            moves = self.possible_moves()


        return moves

    #checks for pins and checks
    def pins_n_checks(self):
        pins = [] # pins where allied pieces in squares and direction from
        checks = [] # squares where check occur
        in_check = False # variable for if in check
        self.gamestatus = False # game status object for determing when in checkmate to know when over
        # if whites turn to move
        if self.white_move: 
            op_colour = "b" #  opponent colour
            ally_colour = "w"
            # start at king locations and work way out checking for checks and pins
            start_row = self.white_king_loc[0] #  sets start row and col
            start_col = self.white_king_loc[1]
        else:
            op_colour = "w"
            ally_colour = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)) # all piece directions 
        for j in range(len(directions)):
            d = directions[j]
            potential_pin = () # reset possible pins

            for i in range(1, 8):
                end_row = start_row + d[0]*i
                end_col = start_col + d[1]*i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece[0] == ally_colour and end_piece[1] != "K":

                        if potential_pin == (): # pin first ally piece
                            potential_pin = (end_row, end_col, d[0], d[1])

                        else: # second allied piece so check possible direction
                            break
                    
                    elif end_piece[0] == op_colour:
                        type = end_piece[1]

                        if (0<=j <= 3 and type =="R") or \
                                (4<=j <= 7 and type =="B") or \
                                (i ==1 and type == "p" and ((op_colour =="w" and 6 <= j <= 7) or (op_colour == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type =="K"):
                            if potential_pin == (): # no blocking piece
                                in_check = True
                                self.gamestatus = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: # piece blocking (a pin)
                                pins.append(potential_pin)
                                self.gamestatus = False
                                break
                        else: # case no check
                            self.gamestatus = False
                            break
                else:
                    break
        #knight checks due to unique pinning and checking types
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == op_colour and end_piece[1] == "N":
                    in_check = True
                    self.gamestatus = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks


    # all moves without considering checks
    def possible_moves(self):
        moves = [] #  store the possible move options in an array 
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_move) or (turn == "b" and not self.white_move): # checks the turn to move correct colour and piece
                    piece = self.board[r][c][1] # determines the piece
                    self.moveFunctions[piece](r, c, moves) # calls the move functions based on piece type
        return moves # return possible moves 

    # pawn moves fucntion using pins to know when a  piece is pinned
    # this means a useer can move pawn ifpiece is not pinned
    def pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direct = ()
        for i in range(len(self.pins) -1, -1, -1): #  code determining the pinned pieces
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direct = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # white pawn moves 
        if self.white_move:
            # one square moves
            if self.board[r-1][c] == "--":
                if not piece_pinned or pin_direct == (-1, 0): #  if piece is not pinned or if pin direction is in direction piece wants to move 
                    moves.append(Move((r, c), (r-1, c), self.board))
                    # two square moves from start position 
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))

            # piece captures diagonallly as pawns do 
            if c-1 >= 0: # left capture
                if self.board[r-1][c-1][0] == "b": # enemy piece capture
                    if not piece_pinned or pin_direct == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # captures to the right
                if self.board[r-1][c+1][0] == "b":
                    if not piece_pinned or pin_direct == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))


        else: # black pawn moves
            if self.board[r+1][c] == "--":#one square move
                if not piece_pinned or pin_direct == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": # 2 square moves
                        moves.append(Move((r, c), (r + 2, c), self.board))


            # piece captures diagonallly as pawns do 
            if c-1 >= 0: # left capture
                if self.board[r+1][c-1][0] == "w": # enemy piece capture
                    if not piece_pinned or pin_direct == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7: # captures to the right
                if self.board[r+1][c+1][0] == "w":
                    if not piece_pinned or pin_direct == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))


    def rook_moves(self,r,c,moves): #  rook moves get the row column and moves passed to it
        piece_pinned = False #  piece pinned bool
        pin_direct = () # pin directions 
        # pin direction and pinned pieces
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c: #  if pins
                piece_pinned = True
                pin_direct = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": # cant remove queen from pin on rook moves
                    self.pins.remove(self.pins[i])
                break

        # how the rook moves
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #  move directions 
        enemy_colour = "b" if self.white_move else "w" #  determine the oponent colour
        # iterate through possible move directions 
        for d in directions:
            # iterate between the board size, 7 squares excluding the square you are on
            for i in range(1,8):
                # calculate rows and coloumns using the row or column direction 
                end_row = r + d[0] * i 
                end_col = c+d[1] * i
                if 0 <= end_row <8 and 0 <= end_col <8: # if on board
                    #if piece not pinned or piece is in pin direction or opposite
                    if not piece_pinned or pin_direct == d or pin_direct == (-d[0], -d[1]): #  for cases so pinned piece can still remain pinned but move away or closer
                        end_piece = self.board[end_row][end_col] # set end piece desired locatiuon
                    if end_piece == "--": # check for empty space
                        moves.append(Move((r, c), (end_row, end_col), self.board)) # append the move 
                    elif end_piece[0] == enemy_colour: # enemy piece valid
                        moves.append(Move((r,c),(end_row, end_col), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # in cases where goes off boeard
                    break
    
    # knight function of how to move
    def knight_moves(self,r,c,moves):
        piece_pinned = False #  piece pinned false
        # determine pins if in a pin
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        # knight move directions 
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_colour = "w" if self.white_move else "b" # determine turn and colour
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8: #  on board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_colour: #  if empty or enemy piece can move to it
                        moves.append(Move((r, c), (end_row, end_col), self.board))


    # Bishop moves function moves diagonal 
    def bishop_moves(self,r,c,moves):
        piece_pinned = False 
        pin_direct = ()
        # See if bishop is pinned 
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direct = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        #move directions
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # diagonal
        enemy_colour = "b" if self.white_move else "w"
        # iterate through them for right one 
        for d in directions:
            for i in range(1, 8): # can move max 7 squares
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # if on board
                    if not piece_pinned or pin_direct == d or pin_direct == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # check for empty space
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_colour:  # enemy piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # in cases where goes off boeard
                    break

    # the queen move function jjust calls the movess from rook and bishop because thats how it can move
    def queen_moves(self, r, c, moves):
        self.rook_moves(r, c, moves) # call rook function
        self.bishop_moves(r, c, moves)# call bishop function


    # the king moves function determining moves from row, column and append new moves to moves list
    def king_moves(self,r,c,moves):
        # to make king move you have to make sure it is not in check in that position 
        # generate king moves 
        row_mov = (-1, -1, -1, 0, 0, 1, 1, 1) 
        col_mov = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_colour = "w" if self.white_move else "b"
        for i in range(8):  # can move max 7 squares
            end_row = r + row_mov[i]
            end_col = c + col_mov[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # if on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_colour:
                    #place king on a square check for checks -  temporary location and check for pins and checks
                    if ally_colour == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    # determines if in that temporary location is in check or not so is a viable move option
                    in_check, pins, checks = self.pins_n_checks()
                    
                    # if the not in check the move is fine to be made
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    # place king back on original location
                    if ally_colour == "w":
                        self.white_king_loc = (r, c)
                    else:
                        self.black_king_loc = (r, c)


class Move():
    # maps keys to values
    # Assigning values for each key
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    ranks_to_ranks = {v:k for k,v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}
    # passes current board state  the start square and end square
    def __init__(self, start_sq, end_sq, board):
        # create move objects 
        self.start_row = start_sq[0] # set start position row from starting row 
        self.start_col = start_sq[1] # set start position column from starting column 
        self.end_row = end_sq[0] # sets end position row as row from end square set previously for ease
        self.end_col = end_sq[1] # sets end position colmn as column from end square 
        self.piece_moved = board[self.start_row][self.start_col] #  know the piece wanting to be moved
        self.piece_taken = board[self.end_row][self.end_col] #  know if the piece captured could be an empty space
        self.pawn_upgrade = False #  if move is a pawn upgrade
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.pawn_upgrade = True
        # keep a move ID to know map moves 
        self.moveID = self.start_row * 1000 + self.start_col*100 + self.end_row*10 + self.end_col
        print(self.moveID)

    # overriding the equals method and defines equality logic
    def __eq__(self, other): #  allows for comparisons of instances 
        if isinstance(other, Move): #  allows for comparison of instance of Move class
            return self.moveID == other.moveID
        return False

    # returns the string of values from starting row and end row to make a chess notation returns rank file notation  
    def getNotation(self):
        return self.get_Rank_File(self.start_row, self.start_col) + self.get_Rank_File(self.end_row, self.end_col)

    # reversed in comparison to chess typical notation
    def get_Rank_File(self, r,c):
        return self.cols_to_files[c]+self.ranks_to_ranks[r]