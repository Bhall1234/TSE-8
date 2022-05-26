import pygame # pygame module
import gtts # Google text to speech module used 
from playsound import playsound # playsound import for check, checkmate
import Chess_engine, Computer # user made python files and modules

WIDTH = HEIGHT = 512 # On screen board size tried several found the ideal resolution
DIMENSION = 8  # 8X8 CHESS BOARD
SQUARE_SIZE = HEIGHT // DIMENSION # calculate square size
IMAGES = {}

# load_images() function to iterate through the 6 types of pieces per colour and load the images
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
 
#draws squares on board, top left square is light. iterates through dimension assigning colour square
def draw_board(screen):
    colours = [pygame.Color("white"), pygame.Color("purple")] #  uses pygame to change colour of board
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r + c) % 2)] #  equation determines colour of square 
            pygame.draw.rect(screen, colour, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE,SQUARE_SIZE)) # draws rectangles of colours to make the board 


# draws pieces on the board by iterating through dimension to assign a piece by using a row and column
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #  if piece is not present on the board 
                screen.blit(IMAGES[piece], pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE,SQUARE_SIZE)) #  draw the piece on the board using .blit 

#graphics within current gamestate may be different depending on last updated board
def drawG_state(screen, gs):
    draw_board(screen) # draw pieces on the board
    draw_pieces(screen, gs.board) # draw pieces onn the board


# This main driver for code
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(pygame.Color("white"))
    gs = Chess_engine.GState()
    validMoves = gs.valid_moves()
    move_made = False # flag variable when move is made
    load_images() # once before whhile loop
    running = True
    sqSelected = () # tracks last square selected
    clicks = [] # keep track of player clicks, tuples in twos
    gameOver = False# game end
    player = True # human playing white
    while running: # game running while loop 
        humanTurn = (gs.white_move and player) # determine who's turn it is for cumputer move

        for event in pygame.event.get():  # get events in a queue
            # Gets the value of the type attribute of the Event object, which is a numerical constant.
            if event.type == pygame.QUIT: #Checks to see if it's equal the numerical constant defined as pygame.QUIT
                running = False # quit game
            # if event type is a mouse button on the pygame window
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If statement runs if the variable game over is False and human turn is True
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos() #locates x,y of mouse
                    # works out column and row location of click based on location coordinates floor divided by the square size
                    col = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE



                    if sqSelected == (row, col) : # in the case where user clicks same square
                        sqSelected = () # deselects
                        clicks =[] # deselects
                    else:
                        # valid click done
                        sqSelected = (row, col) 
                        clicks.append(sqSelected) # append clicks by the square selected to the tuple


                    # When user clicks twice to indicate the piece and location to move to 
                    if len(clicks) == 2: 
                        # Make move 
                        move = Chess_engine.Move(clicks[0], clicks[1], gs.board) # create the move variable
                        for i in range(len(validMoves)):# iterates through the length of the valid move
                            # if statement moves if the chosen and desired move is in the list of valid moves gathered from the game state
                            if move == validMoves[i]: 

                                gs.make_move(move) #  gamestate class called make move function makes the move
                                move_made = True # move_made gets set to True to let system know move is made
                                sqSelected = () # erase user lick
                                clicks = [] #deselects


                        if not move_made: #  if move was not made 
                            clicks = [sqSelected]

            # else if statement makes use of pygame when pressing a key in this case to undo a move on the live screen for testing and other futyure visual integrations
            elif event.type == pygame.KEYDOWN: # 
                if event.key == pygame.K_z: # undo when 'z' pressed
                    gs.undo_move() # calls the undo move function to reset it 
                    move_made = True

        # COmputer oponent move turn
        if not humanTurn and not gameOver:#  if human turn false, if gameover false so still playing
            # gets the move from the Computer.py module function to find tyhe random move passing the validmoves availiable to it
            compMove = Computer.findRandMove(validMoves)
            # after gathering the move calls the make move function with this variable 
            gs.make_move(compMove)
            move_made = True 

        # WHen a move is made using the boolean variable as true
        if move_made:
            # valid moves stores the moves returned by valid moves
            validMoves = gs.valid_moves()
            move_made = False # sets move made to False for next turn

        # Part of loop draws the Screen and updates the pygame display to  be updated using flip() and the draw 
        # games state function
        pygame.display.flip()
        drawG_state(screen, gs)            
            
            
        # if the gamestate object checkmate is True then the game is over
        if gs.checkmate:
            gameOver = True #  sets to True indicating over
            print("GAME DONE CHECKMATE") # prints to let player know game is over
            # Determines if black wins
            if gs.white_move:
                playsound("blackw.mp3") #  uses playsound to play the black win checkmate sound implemented 
                break
            # determines if white wins
            else:
                playsound("whitewin.mp3") #  uses playsound to play the white win checkmate sound implemented 
                break
        # in the case of a stale mate where neither side can win the game (very rare)
        elif gs.stalemate:
            gameOver = True #  also a game over
        




if __name__ == "__main__":
    main()
