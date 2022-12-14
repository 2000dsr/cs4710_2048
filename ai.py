'''Put AI Code Here'''

import copy
from enum import Enum
import random
import game2048


class GenericGameAgent():
    """Base class for other game agents to extend"""

    def __init__(self, gameBoard):
        self.gameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0

    def compute(self):
        '''EACH CLASS SHOULD OVERRIDE THIS'''
        raise NotImplementedError


class DownRightGameAgent(GenericGameAgent):
    """Naive game agent that simply alternates moving Down and Right. Accepts a GameBoard (and maybe other params)"""

    def __init__(self, gameBoard):
        self.gameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0
        self.attempts = 0  # To prevent infinite loops
        # super().__init__(gameBoard)

    def compute(self):
        '''Returns the move that should be done by the agent'''
        # print("Computing next move", self.previousMove, self.moves)
        if (self.previousMove == game2048.Direction.DOWN):
            direction = game2048.Direction.RIGHT
            self.previousMove = direction  # To avoid infinite loops
            if self.gameBoard.check_if_move_legal(direction):

                self.moves += 1
                self.attempts = 0
                return direction
            else:
                self.attempts += 1
                if self.attempts >= 2:
                    # if there have been two consecutive whiffs, move left/right to escape infinite loop
                    self.attempts = 0
                    return game2048.Direction.LEFT

        else:
            direction = game2048.Direction.DOWN
            self.previousMove = direction  # To avoid infinite loops
            if self.gameBoard.check_if_move_legal(direction):
                self.moves += 1

                self.attempts = 0
                return direction
            else:
                self.attempts += 1
                if self.attempts >= 2:
                    # if there have been two consecutive whiffs, move left/right to escape infinite loop
                    self.attempts = 0
                    return game2048.Direction.UP


class RandomGameAgent(GenericGameAgent):
    """Naive game agent that randomly chooses a move different from the previous move. Accepts a GameBoard (and maybe other params)"""

    def __init__(self, gameBoard):
        self.gameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0

    def compute(self):
        '''Returns the move that should be done by the agent'''
        # print("Computing next move", self.previousMove, self.moves)
        randInt = random.randint(1, 4)

        int_to_dir = {1: game2048.Direction.UP, 2: game2048.Direction.DOWN,
                      3: game2048.Direction.LEFT, 4: game2048.Direction.RIGHT}
        direction = int_to_dir[randInt]
        if self.gameBoard.check_if_move_legal(direction):
            self.previousMove = direction
            self.moves += 1
            return direction


class GreedyAgent(GenericGameAgent):
    def __init__(self, gameBoard):
        self.gameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0

    def compute(self):
        '''

        current version just tries to keep bigger numbers in down right corner

        Probably this will be replaced by the minimax agent and minimax agent needs to be improved with better
        heuristics

        '''
        self.moves += 1
        bestMove = None
        maxScore = 0

        for nextMove in game2048.Direction:
            initial = game2048.GameBoard()  # copy of initial board
            for r in range(4):
                for c in range(4):
                    initial.set_value((r, c), self.gameBoard.get_value((r, c)))
            temp_board = game2048.simulate_move(initial, nextMove)
            total = calculate_with_grid(temp_board)
            if total >= maxScore:
                maxScore = total
                bestMove = nextMove

        return bestMove


class MinimaxAgent(GenericGameAgent):
    '''MiniMaxi agent similar to the implementation of our pacman agent.'''

    def __init__(self, gameBoard):
        self.gameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0

    def compute(self):
        '''Returns the move that should be done by the agent'''
        self.moves += 1
        bestMove = None
        maxScore = 0
        for nextMove in game2048.Direction:
            initial = game2048.GameBoard()  # copy of initial board
            for r in range(4):
                for c in range(4):
                    initial.set_value((r, c), self.gameBoard.get_value((r, c)))
                # print("initial board : " + "\n")
                # game2048.print_new_board(initial)
            score = self.calculateScore(initial, nextMove)
            if score >= maxScore:
                maxScore = score
                bestMove = nextMove
        return bestMove

    def calculateScore(self, board, move):
        initial = game2048.GameBoard()  # copy of initial board
        for r in range(4):
            for c in range(4):
                initial.set_value((r, c), board.get_value((r, c)))
        newBoard = game2048.simulate_move(initial, move)
        if game2048.check_boards(board, newBoard):
            return 0
        return self.generateScore(newBoard, 0, 1)

    def generateScore(self, board, depth, depthLimit):
        ''' depthLimit makes sure recursion ends. Could be extended to a greater number than 1 but takes LONG '''
        if depth == depthLimit:
            return self.calculateFinalScore(board)

        total = 0
        for r in range(4):
            for c in range(4):
                if board.get_value((r, c)) == 0:
                    newBoard2 = board
                    newBoard2.set_value((r, c), 2)
                    moveScore2 = self.calculateMoveScore(
                        newBoard2, depth, depthLimit)
                    # proba based on whether new_piece is 2 or 4.
                    total += (0.7*moveScore2)
                    newBoard4 = board
                    newBoard4.set_value((r, c), 4)
                    moveScore4 = self.calculateMoveScore(
                        newBoard4, depth, depthLimit)
                    total += (0.3*moveScore4)
        return total

    def calculateMoveScore(self, board, depth, depthLimit):
        maxScore = 0
        for move in game2048.Direction:
            initial = game2048.GameBoard()  # copy of initial board
            for r in range(4):
                for c in range(4):
                    initial.set_value((r, c), board.get_value((r, c)))
            newBoard = game2048.simulate_move(initial, move)
            if not game2048.check_boards(board, newBoard):
                score = self.generateScore(newBoard, depth+1, depthLimit)
                maxScore = max(score, maxScore)
        return maxScore

    def calculateFinalScore(self, board):
        '''

        similar to evaluation function in pacman
        need to figure out values (different factors?)
        For now, I just listed out what I could think of.

        empty : number of empty GamePiece in board
        totalValue : values of individual GamePiece

        using grid does help with result but still need better.

        from research: smoothness and monotonicity (!!)

        '''
        empty = 0
        for r in range(4):
            for c in range(4):
                if board.get_value((r, c)) == 0:
                    empty += 1

        totalValue = calculate_with_grid(board)

        score = 0.9*empty + 0.1*totalValue
        return score


def calculate_with_grid(board):
    '''

    idea: https://medium.com/@bartoszzadrony/beginners-guide-to-ai-and-writing-your-own-bot-for-the-2048-game-4b8083faaf53

    '''

    score = 0

    gridScore = game2048.GameBoard()
    gridScore.set_value((0, 0), 4**3)
    gridScore.set_value((0, 1), 4**2)
    gridScore.set_value((0, 2), 4**1)
    gridScore.set_value((0, 3), 4**0)
    gridScore.set_value((1, 0), 4**4)
    gridScore.set_value((1, 1), 4**5)
    gridScore.set_value((1, 2), 4**6)
    gridScore.set_value((1, 3), 4**7)
    gridScore.set_value((2, 0), 4**11)
    gridScore.set_value((2, 1), 4**10)
    gridScore.set_value((2, 2), 4**9)
    gridScore.set_value((2, 3), 4**8)
    gridScore.set_value((3, 0), 4**12)
    gridScore.set_value((3, 1), 4**13)
    gridScore.set_value((3, 2), 4**14)
    gridScore.set_value((3, 3), 4**15)

    for r in range(4):
        for c in range(4):
            score += gridScore.get_value((r, c)) * board.get_value((r, c))

    return score


class MonteCarloAgent(GenericGameAgent):
    """Monte Carlo Game Agent
    :cite: https://gabrielromualdo.com/articles/2020-09-12-using-the-monte-carlo-tree-search-algorithm-in-an-ai-to-beat-2048-and-other-games
    this works (on small boards) but is very slow. going to start from scratch
    """

    def __init__(self, gameBoard):
        self.gameBoard: game2048.GameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0
        self.solutionFound = False
        self.solutionList = []
        self.solutionCounter = 0

    def compute(self):
        if not self.solutionFound:
            # if True:
            sims = 500

            move_options = [game2048.Direction.DOWN, game2048.Direction.UP,
                            game2048.Direction.LEFT, game2048.Direction.RIGHT]
            move_scores = [0, 0, 0, 0]
            for move in move_options:
                # print("progress",move)
                if not self.gameBoard.check_if_move_legal(move):
                    continue
                for i in range(sims//4):
                    # print("progress2",i)
                    sim_board: game2048.GameBoard = game2048.GameBoard()

                    sim_board.board = copy.deepcopy(self.gameBoard.board)
                    # print("progress3")
                    # sim_board.print(override=True)
                    # print("VS")
                    # self.gameBoard.print(override=True)
                    sim_board.move(move)
                    start_max = sim_board.max_tile()
                    movements = []
                    moves = 0
                    move_max = 100
                    # while not sim_board.gameover():
                    while moves < move_max and not sim_board.gameover():
                        move2 = sim_board.choose_random_legal_move()
                        # print("MOVING",move2,i)
                        sim_board.move(move2)
                        movements.append(move2)
                        moves += 1
                    # print("GAME OVER")
                    # sim_board.print(override=True)
                    # Because our only goal is to win the game, not maximize score, we simply add 1 if there was a victory
                    if (sim_board.win_game()):
                        print("Game Won!", i, move)
                        sim_board.print(override=True)
                        print("Soln:", movements)
                        self.moves += 1
                        self.previousMove = move
                        self.solutionList = movements
                        self.solutionFound = True
                        return move
                        # We have found a winning solution, so now we will simply feed those moves in!
                    if sim_board.max_tile() > start_max:
                        move_scores[move_options.index(
                            move)] += calculate_with_grid(self.gameBoard)

                    # print("SCORE",move_scores)
            ret_move = move_options[move_scores.index(max(move_scores))]
            # print("AS",move_scores,move_options[move_scores.index(max(move_scores))])
            # print("Returning",ret_move)
            self.moves += 1
            self.previousMove = ret_move
            return ret_move
        else:
            # Runs once solution found is true!

            ret_move = self.solutionList[self.solutionCounter]
            print("Moving piece", ret_move)
            print(self.gameBoard.print(override=True))
            self.solutionCounter += 1

            return ret_move


class MonteCarlo2(GenericGameAgent):
    """
    A second attempt at Monte Carlo
    :cite: https://gsurma.medium.com/2048-solving-2048-with-monte-carlo-tree-search-ai-2dbe76894bab
    """

    def __init__(self, gameBoard):
        self.gameBoard: game2048.GameBoard = gameBoard
        self.previousMove = game2048.Direction.DOWN
        self.moves = 0

    def compute(self):
        runs = 10000
        allResults = []
        move_options = self.gameBoard.get_all_legal_moves()
        for move in move_options:
            for i in range(runs):
                fake_board = copy.deepcopy(self.gameBoard)
                fake_board.move(move)
                move_count = 0
                while (not fake_board.gameover()):
                    fake_board.move(fake_board.choose_random_legal_move())
                    move_count += 1
                # At this point, game is over
                if (fake_board.win_game()):
                    print("GAME WON!!!!")
                    print(move, i)
                    print(self.gameBoard.print(override=True))
                    self.moves += move_count
                    print(self.moves)
                    print("FINAL BOARD")
                    print(fake_board.print(override=True))
                    self.gameBoard.board = fake_board
                    return move
                allResults.append((move, MCboardEvaluation(fake_board)))
        # print(allResults)
        bestDirection = 0
        bestAvgScore = 0
        for dir in move_options:
            denominator = 0
            numerator = 0
            for result in allResults:
                if result[0] == dir:
                    denominator += 1
                    numerator += result[1]
            if denominator != 0 and numerator/denominator > bestAvgScore:
                bestAvgScore = numerator/denominator
                bestDirection = dir
            # print(numerator/denominator, dir)
        self.moves += 1
        self.gameBoard.print(override=True)
        return bestDirection


def MCboardEvaluation(gameBoard):
    """":cite: https://github.com/Kulbear/endless-2048/blob/939479e6ae5d4dae6fb636c9803f8d4ebf5be0e8/agent/minimax_agent.py#L148"""
    empty = gameBoard.get_empty()
    smooth = gameBoard.smoothness()
    mono = gameBoard.monotonicity()
    max_tile = gameBoard.max_tile()

    # return empty + position + weighted_sum + smooth + mono
    return empty + smooth+mono+max_tile
