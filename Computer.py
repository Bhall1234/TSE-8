# computer opponent move file
import random

# allows the computer to sleect a random move from the valid moves given to it making a correct move
def findRandMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)] #  returns random move 
    
